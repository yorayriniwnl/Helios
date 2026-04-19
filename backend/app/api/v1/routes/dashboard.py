from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

try:
    from backend.app.services.dashboard_service import get_summary as service_get_summary
    from backend.app.core.database import get_db
    from backend.app.services.dashboard_service import get_recovery_metrics as service_get_recovery
except Exception:
    from ...services.dashboard_service import get_summary as service_get_summary
    from ...core.database import get_db
    from ...services.dashboard_service import get_recovery_metrics as service_get_recovery

    try:
        from backend.app.services.risk_service import get_risk_summary as service_get_risk
    except Exception:
        from ...services.risk_service import get_risk_summary as service_get_risk


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    return service_get_summary(db)


@router.get("/recovery")
def get_recovery_dashboard(days: int = 30, db: Session = Depends(get_db)):
    return service_get_recovery(db, days=days)


@router.get("/risk")
def get_risk_overview(window_days: int = 7, top_n: int = 20, db: Session = Depends(get_db)):
    """Return predictive risk summary for meters and zones.

    Query params:
    - `window_days`: int, lookback window in days to weigh anomalies (default 7)
    - `top_n`: int, number of top candidate meters to return (default 20)
    """
    return service_get_risk(db, window_days=window_days, top_n=top_n)
