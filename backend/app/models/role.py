"""Role model."""
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

try:
    from backend.app.models.base import BaseModel
except Exception:
    from .base import BaseModel


class Role(BaseModel):
    __tablename__ = "roles"

    name = Column(String(50), nullable=False)
    users = relationship("User", back_populates="role")
