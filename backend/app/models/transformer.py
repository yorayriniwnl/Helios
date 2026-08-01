"""Transformer model."""
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

try:
    from backend.app.models.base import BaseModel
except Exception:
    from .base import BaseModel


class Transformer(BaseModel):
    __tablename__ = "transformers"

    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    capacity = Column(Float, nullable=True)
    load_percent = Column(Float, nullable=True)
    zone = relationship("Zone", back_populates="transformers")
