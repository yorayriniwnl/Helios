from typing import Optional
from pydantic import BaseModel


class RecommendationResponse(BaseModel):
    primary_action: str
    action_text: str
    reason: str
    confidence: float
    meter_id: Optional[int] = None
    zone_id: Optional[int] = None
    alternatives: Optional[list] = []

    model_config = {"from_attributes": True}
