from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class ChatQueryRequest(BaseModel):
    conversation_id: Optional[int] = None
    query: str

class ChatMessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender: str
    message: str
    grounding_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ChatConversationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime
    messages: Optional[List[ChatMessageResponse]] = []

    class Config:
        from_attributes = True
