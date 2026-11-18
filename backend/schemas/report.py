from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class GeneratedReportResponse(BaseModel):
    id: int
    session_id: Optional[int] = None
    user_id: int
    report_type: str
    title: str
    file_path: str
    file_size_bytes: int
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True
