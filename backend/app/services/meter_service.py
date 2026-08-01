from typing import List, Optional
from sqlalchemy.orm import Session

try:
    from backend.app.repositories.meter_repository import (
        create_meter as repo_create_meter,
        get_meter_by_id as repo_get_meter_by_id,
        list_meters as repo_list_meters,
    )
except Exception:
    from ..repositories.meter_repository import (
        create_meter as repo_create_meter,
        get_meter_by_id as repo_get_meter_by_id,
        list_meters as repo_list_meters,
    )


def create_meter(db: Session, meter_number: str, household_name: Optional[str] = None, status: str = "active"):
    return repo_create_meter(db, meter_number=meter_number, household_name=household_name, status=status)


def get_meter_by_id(db: Session, meter_id: int):
    return repo_get_meter_by_id(db, meter_id)


def list_meters(db: Session, skip: int = 0, limit: int = 100) -> List:
    return repo_list_meters(db, skip=skip, limit=limit)
