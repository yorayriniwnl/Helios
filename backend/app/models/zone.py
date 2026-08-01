"""Zone model."""
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

try:
    from backend.app.models.base import BaseModel
except Exception:
    from .base import BaseModel


class Zone(BaseModel):
    __tablename__ = "zones"

    name = Column(String(255), nullable=False, index=True)
    city = Column(String(255), nullable=True)
    state = Column(String(100), nullable=True)
    meters = relationship("Meter", back_populates="zone")
    transformers = relationship("Transformer", back_populates="zone")
