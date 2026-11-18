from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import User, ChatConversation, ChatMessage
from backend.schemas.chat import (
    ChatQueryRequest,
    ChatMessageResponse,
    ChatConversationResponse
)
from backend.services.chat_service import ChatService
from backend.dependencies import get_current_user

router = APIRouter(prefix="/chat", tags=["AI Business Assistant"])

@router.post("/query")
def submit_chat_query(
    request: ChatQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submits a natural language business question to the AI Assistant.
    Answers are verified against and grounded in PostgreSQL database calculations.
    """
    service = ChatService(db)
    result = service.answer_query(
        query=request.query,
        user_id=current_user.id,
        conversation_id=request.conversation_id
    )
    return result

@router.get("/conversations", response_model=List[ChatConversationResponse])
def get_user_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(ChatConversation).filter(ChatConversation.user_id == current_user.id).order_by(ChatConversation.created_at.desc()).all()

@router.get("/conversations/{conversation_id}/messages", response_model=List[ChatMessageResponse])
def get_conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conv = db.query(ChatConversation).filter(
        ChatConversation.id == conversation_id,
        ChatConversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return db.query(ChatMessage).filter(ChatMessage.conversation_id == conversation_id).order_by(ChatMessage.created_at.asc()).all()
