from sqlalchemy.orm import Session

try:
    from backend.app.repositories.user_repository import get_user_by_email
    from backend.app.core.security import verify_password, create_access_token
except Exception:
    from ..repositories.user_repository import get_user_by_email
    from ..core.security import verify_password, create_access_token
try:
    from backend.app.services.audit_service import log_action as svc_log_action
except Exception:
    from ..services.audit_service import log_action as svc_log_action


def login(db: Session, email: str, password: str) -> str:
    """Authenticate user and return an access token.

    Raises ValueError on invalid credentials.
    """
    user = get_user_by_email(db, email)
    if not user:
        raise ValueError("Invalid credentials")
    if not verify_password(password, user.password_hash):
        raise ValueError("Invalid credentials")
    token = create_access_token(user.id)
    # Best-effort audit log for successful login
    try:
        svc_log_action(db, user.id, "user_login", entity="user")
    except Exception:
        pass
    return token
