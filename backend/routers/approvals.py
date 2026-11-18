from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from backend.database import get_db
from backend.models import User, ApprovalRequest, StrategicRecommendation
from backend.schemas.approval import ApprovalRequestResponse, ApprovalDecisionRequest
from backend.dependencies import get_current_user, RoleChecker

router = APIRouter(prefix="/approvals", tags=["Human-in-the-Loop Approvals"])

@router.get("/pending", response_model=List[ApprovalRequestResponse])
def get_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves all pending recommendation approval requests."""
    return db.query(ApprovalRequest).filter(ApprovalRequest.decision == "Pending").order_by(ApprovalRequest.created_at.desc()).all()

@router.get("/all", response_model=List[ApprovalRequestResponse])
def get_all_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves complete approval history (Pending, Approved, Rejected)."""
    return db.query(ApprovalRequest).order_by(ApprovalRequest.created_at.desc()).all()

@router.post("/{request_id}/decision", response_model=ApprovalRequestResponse)
def submit_approval_decision(
    request_id: int,
    decision_in: ApprovalDecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin", "manager"]))
):
    """
    Submits authorized manager decision ('Approved' or 'Rejected') on a strategic proposal.
    Records reviewer user_id, decision timestamp, and manager audit comments.
    """
    decision = decision_in.decision.capitalize()
    if decision not in ["Approved", "Rejected"]:
        raise HTTPException(status_code=400, detail="Decision must be 'Approved' or 'Rejected'.")

    req = db.query(ApprovalRequest).filter(ApprovalRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Approval request not found.")

    req.decision = decision
    req.manager_comments = decision_in.manager_comments
    req.reviewed_by_user_id = current_user.id
    req.decision_date = datetime.utcnow()

    # Also update the linked StrategicRecommendation status
    if req.recommendation:
        req.recommendation.status = decision

    db.commit()
    db.refresh(req)
    return req
