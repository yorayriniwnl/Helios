from typing import Optional
from sqlalchemy.orm import Session

try:
    from backend.app.repositories.user_repository import (
        create_user as repo_create_user,
        get_user_by_email as repo_get_user_by_email,
        get_user_by_id as repo_get_user_by_id,
    )
except Exception:
    from ..repositories.user_repository import (
        create_user as repo_create_user,
        get_user_by_email as repo_get_user_by_email,
        get_user_by_id as repo_get_user_by_id,
    )


def create_user(db: Session, name: str, email: str, password_hash: str, role_id: Optional[int] = None):
    """Create a user after ensuring the email is unique."""
    existing = repo_get_user_by_email(db, email)
    if existing:
        raise ValueError("Email already registered")
    return repo_create_user(db, name=name, email=email, password_hash=password_hash, role_id=role_id)


def get_user(db: Session, user_id: int):
    """Return a user by id."""
    return repo_get_user_by_id(db, user_id)
