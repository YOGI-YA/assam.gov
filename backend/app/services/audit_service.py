import json
import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.models.models import AuditLog

logger = logging.getLogger("govsaarthi.audit_service")

class AuditService:
    @staticmethod
    def log_activity(
        db: Session,
        action: str,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        Records an audit log entry for government compliance and traceability.
        Actions: LOGIN, UPLOAD, DELETE, QUERY, GENERATE_DRAFT, SUMMARIZE
        """
        try:
            meta_str = json.dumps(metadata) if metadata else None
            log_entry = AuditLog(
                user_id=user_id,
                user_email=user_email,
                action=action,
                metadata_json=meta_str
            )
            db.add(log_entry)
            db.commit()
            db.refresh(log_entry)
            logger.info(f"Audit Log [{action}] by user {user_email or user_id or 'system'}")
            return log_entry
        except Exception as e:
            logger.error(f"Failed to record audit log: {e}")
            db.rollback()
            return None

    @staticmethod
    def get_recent_logs(db: Session, limit: int = 50) -> List[AuditLog]:
        return db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()

audit_service = AuditService()
