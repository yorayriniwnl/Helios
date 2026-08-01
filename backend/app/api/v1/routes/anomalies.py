from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

try:
    from backend.app.repositories.anomaly_repository import (
        list_anomaly_events as repo_list_anomalies,
        list_anomaly_events_by_meter as repo_list_anomalies_by_meter,
    )
    from backend.app.schemas.anomaly import AnomalyResponse
    from backend.app.core.database import get_db
except Exception:
    from ...repositories.anomaly_repository import list_anomaly_events as repo_list_anomalies
    from ...repositories.anomaly_repository import list_anomaly_events_by_meter as repo_list_anomalies_by_meter
    from ...schemas.anomaly import AnomalyResponse
    from ...core.database import get_db


router = APIRouter(prefix="/anomalies", tags=["anomalies"])


@router.get("/", response_model=List[AnomalyResponse])
def list_anomalies_route(meter_id: Optional[int] = None, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Return recent anomaly events (newest first). Optionally filter by `meter_id`."""
    if meter_id is not None:
        return repo_list_anomalies_by_meter(db, meter_id=meter_id, skip=skip, limit=limit)
    return repo_list_anomalies(db, skip=skip, limit=limit)
