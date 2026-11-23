from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Document, Message, AuditLog
from app.schemas.schemas import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_docs = db.query(Document).count()
    indexed_docs = db.query(Document).filter(Document.processing_status == "INDEXED").count()
    
    # Count user questions
    total_queries = db.query(Message).filter(Message.role == "user").count()
    
    # Count drafts generated
    total_drafts = db.query(AuditLog).filter(AuditLog.action.in_(["GENERATE_DRAFT", "SUMMARIZE"])).count()

    # Recent questions from actual DB
    recent_msgs = db.query(Message).filter(Message.role == "user").order_by(Message.created_at.desc()).limit(5).all()
    recent_questions = [
        {
            "id": m.id,
            "question": m.content,
            "created_at": m.created_at.isoformat()
        }
        for m in recent_msgs
    ]

    return DashboardStats(
        total_documents=total_docs,
        indexed_documents=indexed_docs,
        total_queries=total_queries,
        total_drafts=total_drafts,
        recent_questions=recent_questions
    )
