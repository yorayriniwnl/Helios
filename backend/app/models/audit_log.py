"""Audit log model for tracking user actions."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func

try:
    from backend.app.models.base import BaseModel
except Exception:
    from .base import BaseModel


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    # The user who initiated the action (optional for system events)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    # Short action name, e.g. "user_login", "alert_resolved"
    action = Column(String(255), nullable=False)
    # The domain entity being acted upon, e.g. "user", "alert", "meter"
    entity = Column(String(255), nullable=False)
    # Optional numeric id of the entity instance
    entity_id = Column(Integer, nullable=True, index=True)
    # Keep the database column name as `metadata`, but avoid the reserved
    # SQLAlchemy attribute name on the mapped class itself.
    metadata_json = Column("metadata", String(2000), nullable=True)
    # Timestamp when the event was recorded
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
