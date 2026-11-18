from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class StrategicRecommendationResponse(BaseModel):
    id: int
    session_id: int
    title: str
    category: str
    description: str
    expected_roi: Optional[str] = None
    risk_level: str
    supporting_evidence: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class ApprovalDecisionRequest(BaseModel):
    decision: str  # "Approved" or "Rejected"
    manager_comments: Optional[str] = None

class ApprovalRequestResponse(BaseModel):
    id: int
    recommendation_id: int
    requested_by_agent: str
    reviewed_by_user_id: Optional[int] = None
    decision: str
    manager_comments: Optional[str] = None
    decision_date: Optional[datetime] = None
    created_at: datetime
    recommendation: Optional[StrategicRecommendationResponse] = None

    class Config:
        from_attributes = True
