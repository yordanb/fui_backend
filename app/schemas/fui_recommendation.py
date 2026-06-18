from datetime import datetime
from pydantic import BaseModel


class RecommendationCreate(BaseModel):
    recommendation_type: str
    instruction: str
    reason: str | None = None
    source: str | None = None


class RecommendationUpdate(BaseModel):
    recommendation_type: str
    instruction: str
    reason: str | None = None
    source: str | None = None
    status: str | None = None


class RecommendationResponse(BaseModel):
    id: int
    fui_id: int

    recommendation_no: int | None = None

    recommendation_type: str | None = None

    instruction: str | None = None

    reason: str | None = None

    source: str | None = None

    status: str | None = None

    created_at: datetime | None = None

    class Config:
        from_attributes = True
