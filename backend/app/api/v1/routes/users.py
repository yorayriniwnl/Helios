from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

try:
    from backend.app.services.user_service import create_user as service_create_user, get_user as service_get_user
    from backend.app.schemas.user import UserCreate, UserResponse
    from backend.app.core.database import get_db
    from backend.app.core.security import hash_password
    from backend.app.dependencies.auth import get_current_user
except Exception:
    from ...services.user_service import create_user as service_create_user, get_user as service_get_user
    from ...schemas.user import UserCreate, UserResponse
    from ...core.database import get_db
    from ...core.security import hash_password
    from ...dependencies.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    # Hash incoming plaintext password before storing
    pw_hash = hash_password(user_in.password)
    try:
        user = service_create_user(db, name=user_in.name, email=user_in.email, password_hash=pw_hash)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: object = Depends(get_current_user)):
    user = service_get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
