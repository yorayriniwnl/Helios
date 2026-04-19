from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

try:
    from backend.app.services.auth_service import login as auth_login
    from backend.app.core.database import get_db
    from backend.app.dependencies.rate_limiter import login_rate_limit
except Exception:
    from ...services.auth_service import login as auth_login
    from ...core.database import get_db
    from ...dependencies.rate_limiter import login_rate_limit

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    # Allow short passwords in tests and development; production should
    # enforce stronger rules elsewhere (e.g., during user creation).
    password: str = Field(...)


class TokenResponse(BaseModel):
    access_token: str


@router.post("/login", response_model=TokenResponse)
def login_route(payload: LoginRequest, db: Session = Depends(get_db), _rl=Depends(login_rate_limit)):
    try:
        token = auth_login(db, payload.email, payload.password)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": token}
