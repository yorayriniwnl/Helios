"""Zone analytics model for storing computed metrics like loss percentage."""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, func, Index

try:
    from backend.app.models.base import BaseModel
except Exception:
    from .base import BaseModel


class ZoneAnalytics(BaseModel):
    __tablename__ = "zone_analytics"

    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=False, index=True)
    window_start = Column(DateTime(timezone=True), nullable=True)
    window_end = Column(DateTime(timezone=True), nullable=True)
    total_input = Column(Float, nullable=True)
    total_consumption = Column(Float, nullable=True)
    loss_percentage = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_zone_analytics_zone_created", "zone_id", "created_at"),
    )
