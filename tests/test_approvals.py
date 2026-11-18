import pytest
from backend.database import SessionLocal
from backend.models import ApprovalRequest, StrategicRecommendation, AnalysisSession, User

def test_approval_workflow_lifecycle():
    db = SessionLocal()
    try:
        # Create a test session
        admin = db.query(User).filter(User.role == "admin").first()
        session = AnalysisSession(user_id=admin.id, status="Verified")
        db.add(session)
        db.commit()

        # Create a test recommendation
        rec = StrategicRecommendation(
            session_id=session.id,
            title="Test Turnaround Action",
            category="Finance",
            description="Reduce deficit store costs",
            status="Pending"
        )
        db.add(rec)
        db.commit()

        # Create pending approval request
        app_req = ApprovalRequest(
            recommendation_id=rec.id,
            requested_by_agent="Strategy Agent",
            decision="Pending"
        )
        db.add(app_req)
        db.commit()
        db.refresh(app_req)

        assert app_req.decision == "Pending"

        # Manager approves
        app_req.decision = "Approved"
        app_req.manager_comments = "Approved by Operations Director"
        app_req.reviewed_by_user_id = admin.id
        rec.status = "Approved"
        db.commit()

        # Verify state transition persisted
        refreshed = db.query(ApprovalRequest).filter(ApprovalRequest.id == app_req.id).first()
        assert refreshed.decision == "Approved"
        assert refreshed.manager_comments == "Approved by Operations Director"
        assert refreshed.recommendation.status == "Approved"

    finally:
        db.close()
