from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BusinessProfileUpdate(BaseModel):
    company_name: Optional[str] = None
    industry: Optional[str] = None
    team_size: Optional[str] = None
    target_margin: Optional[float] = None
    business_goals: Optional[str] = None

class BusinessProfileResponse(BaseModel):
    id: int
    user_id: int
    company_name: str
    industry: str
    team_size: Optional[str] = None
    target_margin: float
    business_goals: Optional[str] = None
    updated_at: datetime

    class Config:
        from_attributes = True
