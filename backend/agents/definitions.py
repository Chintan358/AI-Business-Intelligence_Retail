from crewai import Agent
from backend.agents.llm_provider import get_llm
from backend.agents.tools import (
    get_executive_kpis_tool,
    get_monthly_sales_trend_tool,
    get_category_performance_tool,
    get_channel_performance_tool,
    get_store_pnl_performance_tool,
    get_customer_segments_tool,
    get_stockout_risks_tool,
    get_top_and_slow_products_tool,
    verify_metric_calculation_tool
)

def create_agents(llm=None):
    if llm is None:
        llm = get_llm()

    data_analyst = Agent(
        role="Principal Retail Data Analyst",
        goal="Analyze point-of-sale datasets, calculate actual business KPIs, identify monthly trends (May–October 2026), and detect operational performance anomalies.",
        backstory=(
            "You are an expert retail data scientist with over 15 years of experience in enterprise POS systems and omnichannel sales analytics. "
            "You calculate metrics with absolute mathematical precision using database tools. You never guess figures and uncover variance drivers across months and stores."
        ),
        tools=[
            get_executive_kpis_tool,
            get_monthly_sales_trend_tool,
            get_category_performance_tool,
            get_channel_performance_tool
        ],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    marketing_agent = Agent(
        role="Chief Retail Marketing Strategist",
        goal="Analyze customer segment behavior, repeat purchasing rates, channel-level return leakage, and formulate high-ROI retention and marketing strategies.",
        backstory=(
            "You are an elite retail marketing leader who studies customer lifetime value, cohort repeat rates, and channel return behavior. "
            "You understand that digital return rates above 25% erode profit margins, and you prioritize high-retention customer segments such as Wholesale and Premium tiers."
        ),
        tools=[
            get_customer_segments_tool,
            get_channel_performance_tool
        ],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    finance_agent = Agent(
        role="Retail Financial Controller & Cost Optimization Officer",
        goal="Audit revenue, Cost of Goods Sold (COGS), operating expenses by store and category, calculate profit margins, and identify immediate cost-reduction targets.",
        backstory=(
            "You are a seasoned retail CFO and financial auditor. You analyze contribution margins, detect store-level operating deficits, "
            "and identify disproportionate logistics, rent, and packaging expenses. You ensure that top-line sales growth translates into healthy positive net cash flow."
        ),
        tools=[
            get_executive_kpis_tool,
            get_store_pnl_performance_tool,
            get_category_performance_tool
        ],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    operations_agent = Agent(
        role="VP of Retail Supply Chain & Inventory Operations",
        goal="Audit warehouse inventory levels against safety reorder thresholds, identify stockout hazards, evaluate warehouse movement efficiency, and eliminate logistics waste.",
        backstory=(
            "You are an expert supply chain director with global logistics expertise. You monitor stock balances across 8 regional warehouses, "
            "prevent stockouts of high-velocity SKUs, and streamline warehouse fulfillment to minimize inter-facility transfer costs."
        ),
        tools=[
            get_stockout_risks_tool,
            get_top_and_slow_products_tool
        ],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    strategy_agent = Agent(
        role="Principal Management Turnaround Consultant",
        goal="Synthesize domain findings from Data, Marketing, Finance, and Operations into a coherent 90-day turnaround plan with prioritized strategic actions, expected ROI, and risk assessments.",
        backstory=(
            "You are a senior partner at a tier-1 strategy consulting practice. You excel at taking detailed data, marketing, financial, and supply chain inputs "
            "and forging them into an actionable, board-ready business turnaround plan. You articulate clear rationale and structure consequential proposals for managerial approval."
        ),
        tools=[
            get_executive_kpis_tool
        ],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    verification_agent = Agent(
        role="Chief Audit & Verification Inspector",
        goal="Cross-check all numerical findings, verify mathematical calculations against source data, eliminate LLM hallucinations, and approve or reject the final report.",
        backstory=(
            "You are an adversarial quality assurance auditor. You verify that every single financial metric and KPI cited by other agents matches the verified database ground truth. "
            "You reject reports that contain unsupported claims, exaggerated ROI, or contradictory statements, certifying only 100% audit-proof business intelligence."
        ),
        tools=[
            verify_metric_calculation_tool,
            get_executive_kpis_tool
        ],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    return {
        "data_analyst": data_analyst,
        "marketing_agent": marketing_agent,
        "finance_agent": finance_agent,
        "operations_agent": operations_agent,
        "strategy_agent": strategy_agent,
        "verification_agent": verification_agent
    }
