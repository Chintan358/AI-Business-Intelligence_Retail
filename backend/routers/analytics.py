from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services.kpi_service import KPIService
from backend.dependencies import get_current_user
from backend.models import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/dashboard-payload")
def get_dashboard_payload(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = KPIService(db)
    return {
        "kpis": service.get_executive_kpis(),
        "monthly": service.get_monthly_metrics(),
        "categories": service.get_category_performance(),
        "channels": service.get_channel_performance(),
        "stores": service.get_store_performance()[:5],
        "stockout_alerts": service.get_stockout_alerts(limit=5),
        "products": service.get_top_selling_and_slow_moving_products(limit=5),
        "segments": service.get_customer_segment_insights()
    }
