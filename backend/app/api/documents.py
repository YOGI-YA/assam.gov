import os
import uuid
from typing import List, Optional
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Document, DocumentChunk, User
from app.schemas.schemas import DocumentResponse, DocumentDetail
from app.api.deps import get_current_user, get_current_user_optional
from app.services.document_service import document_service
from app.services.audit_service import audit_service

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form("Office Order"),
    source_classification: str = Form("Public Official Document"),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    content = await file.read()
    filename = file.filename or "uploaded_document.pdf"

    # 1. Validate
    is_valid, err = document_service.validate_pdf_file(filename, content)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    # 2. Create document record
    doc_id = str(uuid.uuid4())
    saved_path = document_service.save_file(doc_id, filename, content)

    doc_record = Document(
        id=doc_id,
        filename=filename,
        file_path=str(saved_path),
        category=category,
        file_size=len(content),
        page_count=0,
        processing_status="PENDING",
        source_classification=source_classification,
        uploaded_by=user.id if user else None
    )
    db.add(doc_record)
    db.commit()
    db.refresh(doc_record)

    # 3. Process & Index
    success, message = document_service.process_and_index_document(db, doc_record)

    # 4. Audit Log
    audit_service.log_activity(
        db, action="DOCUMENT_UPLOAD", 
        user_id=user.id if user else None,
        user_email=user.email if user else "guest",
        metadata={
            "document_id": doc_id,
            "filename": filename,
            "category": category,
            "page_count": doc_record.page_count,
            "status": doc_record.processing_status
        }
    )

    return DocumentResponse.model_validate(doc_record)

@router.get("", response_model=List[DocumentResponse])
def list_documents(
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Document)
    if category and category != "All":
        query = query.filter(Document.category == category)
    if search:
        query = query.filter(Document.filename.ilike(f"%{search}%"))

    docs = query.order_by(Document.created_at.desc()).all()
    return [DocumentResponse.model_validate(d) for d in docs]

@router.get("/{id}", response_model=DocumentDetail)
def get_document(id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    chunk_count = db.query(DocumentChunk).filter(DocumentChunk.document_id == id).count()
    detail = DocumentDetail.model_validate(doc)
    detail.chunk_count = chunk_count
    return detail

@router.delete("/{id}")
def delete_document(
    id: str, 
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    filename = doc.filename
    file_path = Path(doc.file_path)

    # Remove file on disk if exists
    if file_path.exists():
        try:
            os.remove(file_path)
        except Exception:
            pass

    db.delete(doc)
    db.commit()

    audit_service.log_activity(
        db, action="DOCUMENT_DELETE",
        user_id=user.id if user else None,
        user_email=user.email if user else "system",
        metadata={"document_id": id, "filename": filename}
    )

    return {"message": f"Document '{filename}' deleted successfully."}

@router.get("/{id}/file")
def get_document_pdf_file(id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    path = Path(doc.file_path)
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    
    if not path.exists():
        # Check in backend/uploads
        cand1 = Path(__file__).resolve().parent.parent.parent / "uploads" / Path(doc.file_path).name
        if cand1.exists():
            path = cand1
        else:
            # Check in root uploads
            cand2 = Path(__file__).resolve().parent.parent.parent.parent / "uploads" / Path(doc.file_path).name
            if cand2.exists():
                path = cand2
            else:
                # Check sample-data
                cand3 = Path(__file__).resolve().parent.parent.parent.parent / "sample-data" / doc.filename
                if cand3.exists():
                    path = cand3

    if not path.exists():
        raise HTTPException(status_code=404, detail="PDF file missing on server storage.")
    
    return FileResponse(
        path=str(path), 
        media_type="application/pdf", 
        filename=doc.filename,
        content_disposition_type="inline"
    )
