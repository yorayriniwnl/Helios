"""Evidence model for storing case evidence linked to alerts.
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, func

try:
    from backend.app.models.base import BaseModel
except Exception:
    from .base import BaseModel


class Evidence(BaseModel):
    __tablename__ = "evidence"

    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    file_path = Column(String(1000), nullable=False)
    original_filename = Column(String(255), nullable=True)
    gps_lat = Column(Float, nullable=True)
    gps_lon = Column(Float, nullable=True)
    evidence_ts = Column(DateTime(timezone=True), nullable=True)
    notes = Column(String(2000), nullable=True)
    before_after = Column(String(20), nullable=True)  # 'before' or 'after'
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
