from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import (
    User, Customer, Product, Transaction, TransactionItem,
    InventoryMovement, Expense, AnalysisSession, AgentLog,
    ApprovalRequest, GeneratedReport
)
from backend.dependencies import get_current_user, RoleChecker

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])

@router.get("/overview")
def get_admin_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    """Provides high-level system telemetry and record counts for administrators."""
    return {
        "users_count": db.query(User).count(),
        "customers_count": db.query(Customer).count(),
        "products_count": db.query(Product).count(),
        "transactions_count": db.query(Transaction).count(),
        "transaction_items_count": db.query(TransactionItem).count(),
        "inventory_movements_count": db.query(InventoryMovement).count(),
        "expenses_count": db.query(Expense).count(),
        "analysis_sessions_count": db.query(AnalysisSession).count(),
        "agent_logs_count": db.query(AgentLog).count(),
        "approval_requests_count": db.query(ApprovalRequest).count(),
        "reports_count": db.query(GeneratedReport).count()
    }
