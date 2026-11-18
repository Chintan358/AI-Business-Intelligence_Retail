from fastapi import APIRouter, Depends
from backend.dependencies import get_current_user
from backend.models import User

router = APIRouter(prefix="/agents", tags=["Agents"])

@router.get("/list")
def list_specialized_agents(current_user: User = Depends(get_current_user)):
    """Returns technical metadata for all 6 specialized CrewAI agents."""
    return [
        {
            "id": 1,
            "name": "Data Analyst Agent",
            "role": "Principal Retail Data Analyst",
            "goal": "Analyze point-of-sale datasets, calculate actual business KPIs, identify monthly trends (May–October 2026), and detect operational performance anomalies.",
            "backstory": "15+ years experience in retail data systems and econometric variance tracking.",
            "tools": ["get_executive_kpis", "get_monthly_sales_trend", "get_category_performance", "get_channel_performance"],
            "status": "Ready",
            "color": "blue"
        },
        {
            "id": 2,
            "name": "Marketing Agent",
            "role": "Chief Retail Marketing Strategist",
            "goal": "Analyze customer segment behavior, repeat purchasing rates, channel-level return leakage, and formulate high-ROI retention and marketing strategies.",
            "backstory": "Specialist in customer lifetime value (LTV), cohort retention, and return leakage control.",
            "tools": ["get_customer_segments", "get_channel_performance"],
            "status": "Ready",
            "color": "purple"
        },
        {
            "id": 3,
            "name": "Finance Agent",
            "role": "Retail Financial Controller",
            "goal": "Audit revenue, COGS, operating expenses by store and category, calculate profit margins, and identify immediate cost-reduction targets.",
            "backstory": "Former Big Four financial auditor ensuring positive net operating cash flow across 15 store branches.",
            "tools": ["get_executive_kpis", "get_store_pnl_performance", "get_category_performance"],
            "status": "Ready",
            "color": "emerald"
        },
        {
            "id": 4,
            "name": "Operations Agent",
            "role": "VP of Retail Supply Chain",
            "goal": "Audit warehouse inventory levels against safety reorder thresholds, identify stockout hazards, evaluate warehouse movement efficiency, and eliminate logistics waste.",
            "backstory": "Supply chain director managing stock balances across 8 regional warehouses and eliminating transfer delays.",
            "tools": ["get_stockout_risks", "get_top_and_slow_products"],
            "status": "Ready",
            "color": "amber"
        },
        {
            "id": 5,
            "name": "Strategy Agent",
            "role": "Principal Turnaround Consultant",
            "goal": "Synthesize domain findings from Data, Marketing, Finance, and Operations into a coherent 90-day turnaround plan with prioritized strategic actions, expected ROI, and risk assessments.",
            "backstory": "Senior partner at a tier-1 strategy consulting practice specializing in corporate retail turnaround plans.",
            "tools": ["Consumes upstream context from Agents 1, 2, 3, 4"],
            "status": "Ready",
            "color": "indigo"
        },
        {
            "id": 6,
            "name": "Verification Agent",
            "role": "Chief Audit & Verification Inspector",
            "goal": "Cross-check all numerical findings, verify mathematical calculations against source data, eliminate LLM hallucinations, and approve or reject the final report.",
            "backstory": "Adversarial quality assurance auditor certifying 100% mathematical accuracy against database ground truth.",
            "tools": ["verify_metric_calculation", "get_executive_kpis"],
            "status": "Ready",
            "color": "rose"
        }
    ]
