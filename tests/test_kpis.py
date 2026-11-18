import pytest
from backend.database import SessionLocal
from backend.services.kpi_service import KPIService

def test_kpi_calculations_match_ground_truth():
    db = SessionLocal()
    try:
        service = KPIService(db)
        kpis = service.get_executive_kpis()

        # Check total transactions and completed orders
        assert kpis["total_transactions"] == 2500
        assert kpis["completed_orders"] == 1244
        assert kpis["returned_orders"] == 645
        assert kpis["cancelled_orders"] == 611

        # Check net revenue
        assert abs(kpis["net_revenue"] - 109842110.21) < 1.0
        assert abs(kpis["gross_revenue"] - 114717566.35) < 1.0
        assert abs(kpis["discount_amount"] - 4875456.14) < 1.0

        # Check profitability & margins
        assert abs(kpis["gross_profit"] - 24189917.27) < 1.0
        assert abs(kpis["gross_profit_margin_pct"] - 22.02) < 0.1
        assert abs(kpis["total_operating_expenses"] - 28107904.22) < 1.0
        assert abs(kpis["net_operating_profit"] - (-3917986.95)) < 1.0

        # Check customers
        assert kpis["active_customers"] == 779
        assert kpis["repeat_customers"] == 330
        assert abs(kpis["repeat_purchase_rate_pct"] - 42.36) < 0.1

    finally:
        db.close()

def test_monthly_metrics():
    db = SessionLocal()
    try:
        service = KPIService(db)
        monthly = service.get_monthly_metrics()

        assert len(monthly) == 6
        months = [m["month"] for m in monthly]
        assert months == ["2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"]

        # Check September dip
        sep = next(m for m in monthly if m["month"] == "2026-09")
        assert sep["revenue_mom_growth_pct"] < 0
        assert abs(sep["revenue_mom_growth_pct"] - (-14.01)) < 0.2

        # Check October recovery
        oct_data = next(m for m in monthly if m["month"] == "2026-10")
        assert oct_data["revenue_mom_growth_pct"] > 0
        assert abs(oct_data["revenue_mom_growth_pct"] - 21.93) < 0.2

    finally:
        db.close()

def test_category_performance():
    db = SessionLocal()
    try:
        service = KPIService(db)
        categories = service.get_category_performance()

        assert len(categories) == 4
        cat_names = set(c["category"] for c in categories)
        assert cat_names == {"Grocery", "Electronics", "Home", "Fashion"}

        total_rev = sum(c["total_revenue"] for c in categories)
        assert abs(total_rev - 114717566.35) < 1.0

    finally:
        db.close()
