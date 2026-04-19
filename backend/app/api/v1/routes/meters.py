from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

try:
    from backend.app.services.meter_service import (
        create_meter as service_create_meter,
        list_meters as service_list_meters,
        get_meter_by_id as service_get_meter_by_id,
    )
    from backend.app.schemas.meter import MeterCreate, MeterResponse, HighRiskMeterResponse
    from backend.app.core.database import get_db
except Exception:
    from ...services.meter_service import (
        create_meter as service_create_meter,
        list_meters as service_list_meters,
        get_meter_by_id as service_get_meter_by_id,
    )
    from ...schemas.meter import MeterCreate, MeterResponse, HighRiskMeterResponse
    from ...core.database import get_db

router = APIRouter(prefix="/meters", tags=["meters"])


@router.post("/", response_model=MeterResponse)
def create_meter_route(meter_in: MeterCreate, db: Session = Depends(get_db)):
    meter = service_create_meter(
        db,
        meter_number=meter_in.meter_number,
        household_name=meter_in.household_name,
        status=meter_in.status,
    )
    return meter


@router.get("/", response_model=List[MeterResponse])
def list_meters_route(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return service_list_meters(db, skip=skip, limit=limit)


# ── IMPORTANT: static path segments must come BEFORE /{meter_id} ──────────
# FastAPI evaluates routes in declaration order; declaring /{meter_id} first
# would shadow /high-risk and /by-zone/{zone_id}.

@router.get("/high-risk", response_model=List[HighRiskMeterResponse])
def get_high_risk_meters_route(
    window_hours: int = 24,
    threshold: int = 5,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    try:
        from backend.app.services.high_risk_service import get_high_risk_meters as svc_high_risk
    except Exception:
        from ...services.high_risk_service import get_high_risk_meters as svc_high_risk

    try:
        results = svc_high_risk(db, window_hours=window_hours, threshold=threshold, limit=limit)
        return [{"meter_id": r.get("meter_id"), "count": r.get("count")} for r in results]
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to compute high-risk meters")


@router.get("/by-zone/{zone_id}", response_model=List[MeterResponse])
def get_meters_by_zone_route(
    zone_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    try:
        from backend.app.repositories.meter_repository import list_meters_by_zone as repo_list_meters_by_zone
    except Exception:
        from ...repositories.meter_repository import list_meters_by_zone as repo_list_meters_by_zone

    return repo_list_meters_by_zone(db, zone_id=zone_id, skip=skip, limit=limit)


@router.get("/{meter_id}", response_model=MeterResponse)
def get_meter_route(meter_id: int, db: Session = Depends(get_db)):
    meter = service_get_meter_by_id(db, meter_id)
    if not meter:
        raise HTTPException(status_code=404, detail="Meter not found")
    return meter
