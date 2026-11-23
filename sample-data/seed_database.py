import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.core.database import SessionLocal, Base, engine
from app.models.models import Document, User
from app.services.document_service import document_service
from app.services.audit_service import audit_service

def seed_sample_documents():
    # Ensure tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    sample_dir = Path(__file__).resolve().parent

    samples = [
        {
            "filename": "Assam_Secretariat_Manual_of_Office_Procedure.pdf",
            "category": "Rules & Manuals",
            "source_classification": "Official Administrative Secretariat Manual"
        },
        {
            "filename": "DST_ASSAC_Remote_Sensing_Notification.pdf",
            "category": "Department Notifications",
            "source_classification": "Dept. of Science & Technology Gazetted Notification"
        },
        {
            "filename": "AASC_State_Training_Policy_Guidelines.pdf",
            "category": "Training Guidelines",
            "source_classification": "AASC State Administrative Guidelines"
        },
        {
            "filename": "Assam_Pension_Rules_Circular_No_142.pdf",
            "category": "Circulars",
            "source_classification": "Pension & Public Grievances Circular"
        },
        {
            "filename": "Assam Pension Rules, 2024.pdf",
            "source_file": "Assam_Pension_Rules,_2024.pdf",
            "category": "Rules & Manuals",
            "source_classification": "Official State Pension Code",
            "mock_total_pages": 63
        },
        {
            "filename": "Pension Processing Guidelines (OM).pdf",
            "source_file": "Pension_Processing_Guidelines_(OM).pdf",
            "category": "Circulars",
            "source_classification": "Department Office Memorandum",
            "mock_total_pages": 24
        },
        {
            "filename": "Uniform_Solution_Proposal_Requirements_(USPR).pdf",
            "source_file": "uspr.pdf",
            "category": "NESFIC Guidelines",
            "source_classification": "Startup Assam - NESFIC 2026 Official Proposal Standard"
        },
        {
            "filename": "NESFIC_2026_Official_State_Geospatial_and_Open_Data_Resources.pdf",
            "source_file": "NESFIC_2026_Official_State_Geospatial_and_Open_Data_Resources.pdf",
            "category": "State Data Portals",
            "source_classification": "NESFIC 2026 Public Geospatial & Open Data Compendium"
        },
        {
            "filename": "ASDMA_Disaster_Management_SOP_and_Relief_Manual.pdf",
            "source_file": "ASDMA_Disaster_Management_SOP_and_Relief_Manual.pdf",
            "category": "Disaster Management Guidelines",
            "source_classification": "Assam State Disaster Management Authority Official SOP & SDRF Manual"
        }
    ]

    try:
        user = db.query(User).filter(User.role == "admin").first()
        user_id = user.id if user else None

        for s in samples:
            src_name = s.get("source_file", s["filename"])
            pdf_path = sample_dir / src_name
            if not pdf_path.exists():
                print(f"Skipping {src_name}, file not found.")
                continue

            existing = db.query(Document).filter(Document.filename == s["filename"]).first()

            with open(pdf_path, "rb") as f:
                content = f.read()

            import uuid
            doc_id = existing.id if existing else str(uuid.uuid4())
            saved_path = document_service.save_file(doc_id, s["filename"], content)

            if not existing:
                doc_record = Document(
                    id=doc_id,
                    filename=s["filename"],
                    file_path=str(saved_path),
                    category=s["category"],
                    file_size=len(content),
                    page_count=0,
                    processing_status="PENDING",
                    source_classification=s["source_classification"],
                    uploaded_by=user_id
                )
                db.add(doc_record)
                db.commit()
                db.refresh(doc_record)
            else:
                doc_record = existing
                doc_record.file_path = str(saved_path)
                doc_record.processing_status = "PENDING"
                db.commit()

            success, msg = document_service.process_and_index_document(db, doc_record)
            print(f"Indexed {s['filename']}: status={doc_record.processing_status}, pages={doc_record.page_count}")

            audit_service.log_activity(
                db, action="DOCUMENT_UPLOAD", user_id=user_id, user_email="admin@aasc.assam.gov.in",
                metadata={"filename": s["filename"], "category": s["category"], "pages": doc_record.page_count}
            )

    except Exception as e:
        print(f"Error seeding documents: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_sample_documents()
