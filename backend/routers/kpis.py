from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from backend.database import get_db
from backend.services.kpi_service import KPIService
from backend.schemas.kpi import (
    ExecutiveKPIResponse,
    MonthlyMetricItem,
    CategoryPerformanceItem,
    ChannelPerformanceItem,
    StorePerformanceItem,
    StockoutAlertItem
)
from backend.dependencies import get_current_user
from backend.models import User

router = APIRouter(prefix="/kpis", tags=["KPIs & Analytics Engine"])

@router.get("/summary", response_model=ExecutiveKPIResponse)
def get_executive_summary_kpis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = KPIService(db)
    return service.get_executive_kpis()

@router.get("/monthly", response_model=List[MonthlyMetricItem])
def get_monthly_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = KPIService(db)
    return service.get_monthly_metrics()

@router.get("/categories", response_model=List[CategoryPerformanceItem])
def get_category_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = KPIService(db)
    return service.get_category_performance()

@router.get("/channels", response_model=List[ChannelPerformanceItem])
def get_channel_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = KPIService(db)
    return service.get_channel_performance()

@router.get("/stores", response_model=List[StorePerformanceItem])
def get_store_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = KPIService(db)
    return service.get_store_performance()

@router.get("/segments")
def get_customer_segments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = KPIService(db)
    return service.get_customer_segment_insights()

@router.get("/stockout-alerts", response_model=List[StockoutAlertItem])
def get_stockout_alerts(
    limit: int = 15,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = KPIService(db)
    return service.get_stockout_alerts(limit=limit)

@router.get("/products/top-slow")
def get_top_slow_products(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = KPIService(db)
    return service.get_top_selling_and_slow_moving_products(limit=limit)
