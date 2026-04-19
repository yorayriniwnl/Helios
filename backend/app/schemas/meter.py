from typing import Optional
from pydantic import BaseModel


class MeterCreate(BaseModel):
    meter_number: str
    household_name: Optional[str] = None
    status: str = "active"
    zone_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class MeterResponse(BaseModel):
    id: int
    meter_number: str
    household_name: Optional[str] = None
    status: str
    zone_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    model_config = {"from_attributes": True}


class HighRiskMeterResponse(BaseModel):
    meter_id: int
    count: int

    model_config = {"from_attributes": True}
