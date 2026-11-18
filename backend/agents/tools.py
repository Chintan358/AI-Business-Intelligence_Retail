import json
from crewai.tools import tool
from backend.database import SessionLocal
from backend.services.kpi_service import KPIService

@tool("get_executive_kpis")
def get_executive_kpis_tool() -> str:
    """
    Retrieves the verified executive business KPIs for the retail enterprise spanning May 1, 2026 to October 31, 2026.
    Returns: Gross Revenue, Net Revenue, Discounts, Completed Orders, AOV, COGS, Gross Profit, Gross Margin %, OpEx, Net Operating Margin, Return Rate, Cancellation Rate.
    """
    db = SessionLocal()
    try:
        service = KPIService(db)
        kpis = service.get_executive_kpis()
        return json.dumps(kpis, indent=2)
    finally:
        db.close()

@tool("get_monthly_sales_trend")
def get_monthly_sales_trend_tool() -> str:
    """
    Retrieves month-by-month financial performance metrics for May, June, July, August, September, and October 2026.
    Returns: Monthly Net Revenue, Orders, COGS, Gross Profit, Gross Margin %, Operating Expenses, Net Operating Profit, and MoM Growth %.
    """
    db = SessionLocal()
    try:
        service = KPIService(db)
        trends = service.get_monthly_metrics()
        return json.dumps(trends, indent=2)
    finally:
        db.close()

@tool("get_category_performance")
def get_category_performance_tool() -> str:
    """
    Retrieves sales and profitability breakdown across all four retail departments: Grocery, Electronics, Home, and Fashion.
    Returns: Category Revenue, Units Sold, COGS, Gross Profit, and Gross Margin %.
    """
    db = SessionLocal()
    try:
        service = KPIService(db)
        cats = service.get_category_performance()
        return json.dumps(cats, indent=2)
    finally:
        db.close()

@tool("get_channel_performance")
def get_channel_performance_tool() -> str:
    """
    Retrieves sales channel metrics across In-store, Mobile App, and Online.
    Returns: Orders, Net Revenue, Returned Orders, Return Rate %, Cancelled Orders, Cancellation Rate %, and Returned Lost Revenue.
    """
    db = SessionLocal()
    try:
        service = KPIService(db)
        channels = service.get_channel_performance()
        return json.dumps(channels, indent=2)
    finally:
        db.close()

@tool("get_store_pnl_performance")
def get_store_pnl_performance_tool() -> str:
    """
    Retrieves branch-level P&L for all 15 retail stores (STR01 to STR15).
    Returns: Store Net Revenue, Orders, Store COGS, Allocated Store Operating Expenses, Gross Profit, and Net Operating Profit.
    """
    db = SessionLocal()
    try:
        service = KPIService(db)
        stores = service.get_store_performance()
        return json.dumps(stores, indent=2)
    finally:
        db.close()

@tool("get_customer_segments")
def get_customer_segments_tool() -> str:
    """
    Retrieves customer cohort behavior across Regular, New, Wholesale, and Premium segments.
    Returns: Orders, Unique Customers, Net Revenue, AOV, and Revenue Share %.
    """
    db = SessionLocal()
    try:
        service = KPIService(db)
        segments = service.get_customer_segment_insights()
        return json.dumps(segments, indent=2)
    finally:
        db.close()

@tool("get_stockout_risks")
def get_stockout_risks_tool() -> str:
    """
    Audits warehouse inventory levels against product safety reorder thresholds.
    Returns: List of SKUs where current stock is less than or equal to reorder level, deficit units, category, and supplier ID.
    """
    db = SessionLocal()
    try:
        service = KPIService(db)
        alerts = service.get_stockout_alerts(limit=15)
        return json.dumps(alerts, indent=2)
    finally:
        db.close()

@tool("get_top_and_slow_products")
def get_top_and_slow_products_tool() -> str:
    """
    Retrieves best-selling SKUs by net revenue and slowest-moving SKUs by unit volume.
    """
    db = SessionLocal()
    try:
        service = KPIService(db)
        prods = service.get_top_selling_and_slow_moving_products(limit=10)
        return json.dumps(prods, indent=2)
    finally:
        db.close()

@tool("verify_metric_calculation")
def verify_metric_calculation_tool(metric_name: str, claimed_value: float) -> str:
    """
    Cross-checks a specific analytical or financial claim against database ground truth.
    Supported metric_name values: 'net_revenue', 'gross_revenue', 'cogs', 'gross_profit', 'total_opex', 'completed_orders', 'aov'.
    """
    db = SessionLocal()
    try:
        service = KPIService(db)
        kpis = service.get_executive_kpis()
        clean_key = metric_name.strip().lower()
        if clean_key in kpis:
            true_val = float(kpis[clean_key])
            diff = abs(true_val - float(claimed_value))
            pct_err = (diff / true_val * 100) if true_val != 0 else 0
            is_valid = pct_err < 0.5  # within 0.5% tolerance
            return json.dumps({
                "metric": clean_key,
                "claimed_value": claimed_value,
                "ground_truth_value": true_val,
                "difference": round(diff, 2),
                "is_valid": is_valid,
                "status": "VERIFIED_MATCH" if is_valid else "DISCREPANCY_FLAGGED"
            })
        return json.dumps({"error": f"Metric '{metric_name}' not found in standard KPI engine."})
    finally:
        db.close()
