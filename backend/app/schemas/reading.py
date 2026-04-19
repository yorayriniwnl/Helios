from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReadingCreate(BaseModel):
    meter_id: int
    timestamp: datetime
    voltage: Optional[float] = None
    current: Optional[float] = None
    power_consumption: Optional[float] = None


class ReadingResponse(BaseModel):
    id: int
    meter_id: int
    timestamp: datetime
    voltage: Optional[float] = None
    current: Optional[float] = None
    power_consumption: Optional[float] = None

    model_config = {"from_attributes": True}
