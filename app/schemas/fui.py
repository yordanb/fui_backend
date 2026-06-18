from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from typing import List

class FuiCreate(BaseModel):
    unit_number: str
    priority_level: Optional[str] = None


class FuiUpdate(BaseModel):
    unit_number: str
    priority_level: Optional[str] = None


class FuiResponse(BaseModel):
    id: int
    fui_number: str
    unit_number: str
    priority_level: Optional[str]

    status: str

    created_by: int

    created_at: Optional[datetime]
    submitted_at: Optional[datetime]
    approved_at: Optional[datetime]
    closed_at: Optional[datetime]

    class Config:
        from_attributes = True


class FuiStatusUpdate(BaseModel):
    status: str

class FuiListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[FuiResponse]
