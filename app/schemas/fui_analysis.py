from datetime import datetime
from pydantic import BaseModel
from datetime import datetime
from typing import Optional



class FuiAnalysisCreate(BaseModel):
    analysis_type: str | None = None
    problem_description: str
    root_cause: str | None = None
    impact_analysis: str | None = None
    corrective_action: str | None = None


class FuiAnalysisUpdate(BaseModel):
    analysis_type: str | None = None
    problem_description: str | None = None
    root_cause: str | None = None
    impact_analysis: str | None = None
    corrective_action: str | None = None


class FuiAnalysisResponse(BaseModel):
    id: int
    fui_id: int

    analysis_type: str | None
    problem_description: str
    root_cause: str | None
    impact_analysis: str | None
    corrective_action: str | None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
