from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class StartAnalysisRequest(BaseModel):
    dataset_id: Optional[int] = None
    custom_instructions: Optional[str] = None

class AgentLogResponse(BaseModel):
    id: int
    session_id: int
    agent_name: str
    agent_role: str
    task_name: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_duration_sec: float
    output_text: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class AnalysisSessionResponse(BaseModel):
    id: int
    user_id: int
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_duration_sec: float
    executive_summary: Optional[str] = None
    is_verified: bool
    verification_scorecard: Optional[Dict[str, Any]] = None
    consolidated_plan: Optional[Dict[str, Any]] = None
    agent_logs: Optional[List[AgentLogResponse]] = []
    created_at: datetime

    class Config:
        from_attributes = True
