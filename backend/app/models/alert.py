"""Alert model."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func, Boolean

try:
    from backend.app.models.base import BaseModel
except Exception:
    from .base import BaseModel


class Alert(BaseModel):
    __tablename__ = "alerts"

    meter_id = Column(Integer, ForeignKey("meters.id"), nullable=True, index=True)
    reading_id = Column(Integer, ForeignKey("readings.id"), nullable=True, index=True)
    type = Column(String(100), nullable=False)
    score = Column(Float, nullable=True)
    explanation = Column(String(1000), nullable=True)
    severity = Column(String(50), nullable=False, default="medium", index=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    status = Column(String(50), nullable=False, default="open", index=True)
    resolution_notes = Column(String(2000), nullable=True)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    sla_breached = Column(Boolean, nullable=False, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
