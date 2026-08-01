from typing import Optional
from pydantic import BaseModel


class ZoneCreate(BaseModel):
    name: str
    city: Optional[str] = None
    state: Optional[str] = None


class ZoneResponse(BaseModel):
    id: int
    name: str
    city: Optional[str] = None
    state: Optional[str] = None

    model_config = {"from_attributes": True}


class ZoneOverview(BaseModel):
    """Zone with enriched runtime metrics — returned by /zones/overview."""
    id: int
    name: str
    city: Optional[str] = None
    state: Optional[str] = None
    meter_count: int = 0
    alert_count: int = 0
    anomaly_count: int = 0
    anomaly_density: float = 0.0
    zone_loss_percentage: float = 0.0
    risk: str = "low"

    model_config = {"from_attributes": True}
