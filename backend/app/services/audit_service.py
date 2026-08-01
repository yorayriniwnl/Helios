from typing import Optional
from sqlalchemy.orm import Session

try:
    from backend.app.repositories.audit_repository import create_audit_log as repo_create_audit_log
except Exception:
    from ..repositories.audit_repository import create_audit_log as repo_create_audit_log


def log_action(
    db: Session,
    user_id: Optional[int],
    action: str,
    entity: str = "user",
    entity_id: Optional[int] = None,
    metadata: Optional[dict] = None,
):
    """Log an action to the audit log (best-effort).

    Returns the created AuditLog or None on failure. Accepts optional
    `entity_id` and `metadata` for richer context.
    """
    try:
        return repo_create_audit_log(db, user_id=user_id, action=action, entity=entity, entity_id=entity_id, metadata=metadata)
    except Exception:
        return None
