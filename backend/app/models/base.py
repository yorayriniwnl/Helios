"""Base SQLAlchemy model with auto timestamps."""
from sqlalchemy import Column, Integer, DateTime, func

# Try absolute import first, fall back to relative import when used as a package
try:
    from backend.app.core.database import Base
except Exception:
    from ..core.database import Base


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), default=func.now(), onupdate=func.now(), nullable=False)
