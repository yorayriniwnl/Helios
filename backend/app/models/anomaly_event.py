"""Anomaly event model."""
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, func

try:
    from backend.app.models.base import BaseModel
except Exception:
    from .base import BaseModel


class AnomalyEvent(BaseModel):
    __tablename__ = "anomaly_events"

    meter_id = Column(Integer, ForeignKey("meters.id"), nullable=True, index=True)
    reading_id = Column(Integer, ForeignKey("readings.id"), nullable=True, index=True)
    type = Column(String(100), nullable=False)
    score = Column(Float, nullable=True)
    explanation = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
