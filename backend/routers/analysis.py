from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import User, AnalysisSession, AgentLog
from backend.schemas.analysis import StartAnalysisRequest, AnalysisSessionResponse, AgentLogResponse
from backend.agents.crew_runner import run_multi_agent_analysis
from backend.dependencies import get_current_user

router = APIRouter(prefix="/analysis", tags=["AI Business Analysis"])

@router.post("/start", response_model=AnalysisSessionResponse)
def start_analysis_session(
    request: StartAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Spawns an asynchronous CrewAI multi-agent execution session.
    The six agents run collaboratively in the background, logging status in real time.
    """
    new_session = AnalysisSession(
        user_id=current_user.id,
        dataset_id=request.dataset_id,
        status="Pending"
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    # Launch execution in background task
    background_tasks.add_task(run_multi_agent_analysis, new_session.id)
    return new_session

@router.get("/sessions", response_model=List[AnalysisSessionResponse])
def list_analysis_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sessions = db.query(AnalysisSession).order_by(AnalysisSession.created_at.desc()).all()
    return sessions

@router.get("/sessions/{session_id}", response_model=AnalysisSessionResponse)
def get_session_details(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(AnalysisSession).filter(AnalysisSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Analysis session not found.")
    return session

@router.get("/sessions/{session_id}/logs", response_model=List[AgentLogResponse])
def get_session_agent_logs(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logs = db.query(AgentLog).filter(AgentLog.session_id == session_id).order_by(AgentLog.id.asc()).all()
    return logs
