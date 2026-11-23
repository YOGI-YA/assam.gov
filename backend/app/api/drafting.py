from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Document, User
from app.schemas.schemas import DraftingRequest, DraftingResponse, SummarizeRequest, CitationItem
from app.api.deps import get_current_user_optional
from app.services.retrieval_service import retrieval_service
from app.services.llm_service import llm_service
from app.services.audit_service import audit_service

router = APIRouter(prefix="/drafting", tags=["Drafting Studio"])

@router.post("/generate", response_model=DraftingResponse)
def generate_draft(
    req: DraftingRequest,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    # Retrieve relevant references if documents were specified or search query based on subject
    references: List[CitationItem] = []
    query_text = f"{req.subject} {req.instructions}"

    if req.document_ids:
        for doc_id in req.document_ids:
            cits = retrieval_service.retrieve_relevant_chunks(db, query=query_text, document_id=doc_id, top_k=2)
            references.extend(cits)
    else:
        # Search all documents for relevant context
        references = retrieval_service.retrieve_relevant_chunks(db, query=query_text, top_k=3)

    draft_text = llm_service.generate_draft(req, references)

    # Record audit log
    audit_service.log_activity(
        db, action="GENERATE_DRAFT",
        user_id=user.id if user else None,
        user_email=user.email if user else "officer",
        metadata={
            "draft_type": req.draft_type,
            "subject": req.subject,
            "references_count": len(references)
        }
    )

    return DraftingResponse(
        draft_type=req.draft_type,
        subject=req.subject,
        draft_content=draft_text,
        references_used=references,
        disclaimer="DRAFT ONLY — Requires human review, verification and authorized signature before issuance.",
        created_at=datetime.utcnow()
    )

@router.post("/summarize", response_model=DraftingResponse)
def summarize_document(
    req: SummarizeRequest,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    doc = db.query(Document).filter(Document.id == req.document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Retrieve major chunks from document
    cits = retrieval_service.retrieve_relevant_chunks(
        db, query="rules objectives procedure powers sanction overview", document_id=doc.id, top_k=5, threshold=0.0
    )

    draft_req = DraftingRequest(
        draft_type="summary",
        subject=f"Executive Summary of {doc.filename}",
        instructions=f"Provide a structured administrative summary of the document {doc.filename} ({doc.category}, {doc.page_count} pages).",
        document_ids=[doc.id]
    )

    draft_text = llm_service.generate_draft(draft_req, cits)

    audit_service.log_activity(
        db, action="SUMMARIZE",
        user_id=user.id if user else None,
        user_email=user.email if user else "officer",
        metadata={"document_id": doc.id, "filename": doc.filename}
    )

    return DraftingResponse(
        draft_type="summary",
        subject=draft_req.subject,
        draft_content=draft_text,
        references_used=cits,
        disclaimer="DRAFT ONLY — Generated executive summary for administrative reference.",
        created_at=datetime.utcnow()
    )
