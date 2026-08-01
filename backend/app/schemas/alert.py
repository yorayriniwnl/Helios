from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: int
    meter_id: Optional[int] = None
    reading_id: Optional[int] = None
    type: str
    score: Optional[float] = None
    explanation: Optional[str] = None
    assigned_to: Optional[int] = None
    status: str
    severity: Optional[str] = "medium"
    responded_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    sla_breached: Optional[bool] = False
    created_at: datetime
    decision: Optional[Dict[str, Any]] = None

    model_config = {"from_attributes": True}


class PriorityAlertResponse(BaseModel):
    id: int
    meter_id: Optional[int] = None
    type: str
    score: Optional[float] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    priority_score: float
    components: Dict[str, Any]

    model_config = {"from_attributes": True}
