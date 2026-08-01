"""Meter model."""
from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

try:
    from backend.app.models.base import BaseModel
except Exception:
    from .base import BaseModel


class Meter(BaseModel):
    __tablename__ = "meters"

    meter_number    = Column(String(100), unique=True, index=True, nullable=False)
    household_name  = Column(String(255), nullable=True)
    status          = Column(String(50),  nullable=False, default="active")
    zone_id         = Column(Integer, ForeignKey("zones.id"), nullable=True, index=True)

    # Geospatial coordinates for map/heatmap layers
    latitude        = Column(Float, nullable=True)
    longitude       = Column(Float, nullable=True)

    zone = relationship("Zone", back_populates="meters")
