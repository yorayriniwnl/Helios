from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

try:
    from backend.app.services.reading_service import (
        create_reading as service_create_reading,
        get_readings_by_meter as service_get_readings_by_meter,
    )
    from backend.app.schemas.reading import ReadingCreate, ReadingResponse
    from backend.app.core.database import get_db
    from backend.app.dependencies.rate_limiter import readings_rate_limit
except Exception:
    from ...services.reading_service import (
        create_reading as service_create_reading,
        get_readings_by_meter as service_get_readings_by_meter,
    )
    from ...schemas.reading import ReadingCreate, ReadingResponse
    from ...core.database import get_db
    from ...dependencies.rate_limiter import readings_rate_limit

router = APIRouter(prefix="/readings", tags=["readings"])


@router.post("/", response_model=ReadingResponse)
def create_reading_route(reading_in: ReadingCreate, db: Session = Depends(get_db), _rl=Depends(readings_rate_limit)):
    reading = service_create_reading(
        db,
        meter_id=reading_in.meter_id,
        timestamp=reading_in.timestamp,
        voltage=reading_in.voltage,
        current=reading_in.current,
        power_consumption=reading_in.power_consumption,
    )
    return reading


@router.get("/by-meter/{meter_id}", response_model=List[ReadingResponse])
def get_readings_by_meter_route(meter_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return service_get_readings_by_meter(db, meter_id=meter_id, skip=skip, limit=limit)
