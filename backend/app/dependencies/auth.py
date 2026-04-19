from typing import Any
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

try:
    from backend.app.core.security import decode_token
    from backend.app.core.database import get_db
    from backend.app.repositories.user_repository import get_user_by_id
except Exception:
    from ..core.security import decode_token
    from ..core.database import get_db
    from ..repositories.user_repository import get_user_by_id


_bearer = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(_bearer), db: Session = Depends(get_db)) -> Any:
    """Validate bearer token and return the authenticated user.

    Raises HTTPException(401) when token is missing/invalid or user not found.
    """
    token = None
    try:
        token = credentials.credentials
    except Exception:
        raise HTTPException(status_code=401, detail="Missing authentication token")

    try:
        payload = decode_token(token)
        user_id = int(payload.get("user_id"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
