import json
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import AuditLog
from app.schemas.schemas import AuditLogResponse

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])

@router.get("", response_model=List[AuditLogResponse])
def get_audit_logs(limit: int = 50, db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    res = []
    for log in logs:
        meta_dict = None
        if log.metadata_json:
            try:
                meta_dict = json.loads(log.metadata_json)
            except Exception:
                meta_dict = {"raw": log.metadata_json}
        res.append(AuditLogResponse(
            id=log.id,
            user_id=log.user_id,
            user_email=log.user_email,
            action=log.action,
            metadata=meta_dict,
            created_at=log.created_at
        ))
    return res
