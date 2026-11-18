from crewai import Task

def create_tasks(agents: dict) -> list[Task]:
    task_data_analysis = Task(
        description=(
            "1. Query the database using `get_executive_kpis` and `get_monthly_sales_trend`.\n"
            "2. Document verified total net revenue, gross profit, completed order counts, and AOV for the May 1 – October 31, 2026 dataset.\n"
            "3. Analyze the monthly performance trajectory: explain the specific drivers behind the September revenue decline (-14.0%) and October recovery (+21.9%).\n"
            "4. Analyze category mix using `get_category_performance` and channel volume using `get_channel_performance`.\n"
            "5. Produce a structured analytical summary with exact numerical figures."
        ),
        expected_output=(
            "A structured Analytical Findings Report detailing verified top-line KPIs, monthly performance variances, "
            "category breakdowns, and identified anomalies grounded strictly in database calculations."
        ),
        agent=agents["data_analyst"]
    )

    task_marketing = Task(
        description=(
            "1. Review the data analysis findings and query `get_customer_segments` and `get_channel_performance`.\n"
            "2. Evaluate customer cohort behavior across Regular, New, Wholesale, and Premium segments.\n"
            "3. Analyze customer repeat purchase rates and identify why digital channels (Online and Mobile App) suffer from ~28% return rates compared to in-store.\n"
            "4. Formulate targeted retention strategies for Wholesale accounts in key cities (Surat, Mumbai, Rajkot) and recommend promotions to curb digital return leakage."
        ),
        expected_output=(
            "A comprehensive Marketing & Customer Intelligence Report containing segment analysis, repeat purchase behavior, "
            "channel return leakage assessment, and targeted growth and retention strategies."
        ),
        agent=agents["marketing_agent"],
        context=[task_data_analysis]
    )

    task_finance = Task(
        description=(
            "1. Review top-line findings and query `get_store_pnl_performance` and `get_executive_kpis`.\n"
            "2. Analyze Cost of Goods Sold (COGS: ₹85.65M) and Gross Margin (22.02%) across retail categories.\n"
            "3. Audit total store operating expenses (₹28.11M): breakdown Marketing, Rent, Staff Salaries, Logistics, Packaging, and Utilities.\n"
            "4. Diagnose the net operating loss (-₹3.92M) and identify specific deficit stores (such as STR03, STR09, STR13).\n"
            "5. Recommend immediate cost optimization and margin enhancement measures to achieve positive operating profitability."
        ),
        expected_output=(
            "A detailed Financial Intelligence Report outlining P&L performance, operating expense drivers, store deficit diagnostics, "
            "and cost rationalization recommendations."
        ),
        agent=agents["finance_agent"],
        context=[task_data_analysis]
    )

    task_operations = Task(
        description=(
            "1. Query `get_stockout_risks` and `get_top_and_slow_products`.\n"
            "2. Audit inventory health across the 8 fulfillment warehouses: identify products with current stock at or below reorder levels.\n"
            "3. Examine warehouse stock movement logs (1,800 movements) to detect logistics bottlenecks and inter-facility transfer waste.\n"
            "4. Formulate an inventory replenishment plan for critical stockout risks and recommend strategies to accelerate slow-moving merchandise."
        ),
        expected_output=(
            "An Operational & Supply Chain Report listing stockout hazards, warehouse velocity diagnostics, and replenishment recommendations."
        ),
        agent=agents["operations_agent"],
        context=[task_data_analysis]
    )

    task_strategy = Task(
        description=(
            "1. Synthesize domain outputs from Data Analyst, Marketing, Finance, and Operations agents.\n"
            "2. Construct a unified, cohesive 90-day Retail Turnaround Action Plan addressing:\n"
            "   - Return & cancellation leakage reduction (recovering up to ₹25M in realized sales).\n"
            "   - Operating cost rationalization in deficit stores (eliminating ₹2.4M in store overhead waste).\n"
            "   - Regional wholesale loyalty programs in high-density markets (Surat, Mumbai, Rajkot).\n"
            "   - Rapid stock replenishment for 15+ high-risk stockout SKUs.\n"
            "3. Formulate four prioritized, actionable business proposals suitable for Human-in-the-Loop executive approval with expected ROI and risk disclosures."
        ),
        expected_output=(
            "A Master Business Turnaround Strategy containing an executive summary, prioritized recommendations, expected financial impact, "
            "and structured proposals for managerial review."
        ),
        agent=agents["strategy_agent"],
        context=[task_data_analysis, task_marketing, task_finance, task_operations]
    )

    task_verification = Task(
        description=(
            "1. Ingest the consolidated turnaround strategy and invoke `verify_metric_calculation` and `get_executive_kpis`.\n"
            "2. Audit every single numerical assertion in the strategy against source database calculations:\n"
            "   - Verify Net Revenue (₹109,842,110.21).\n"
            "   - Verify Completed Transactions (1,244).\n"
            "   - Verify Gross Profit (₹24,189,917.27) and Margin (22.02%).\n"
            "   - Verify OpEx (₹28,107,904.22) and Operating Deficit (-₹3,917,986.95).\n"
            "3. Verify that ROI claims are logically supported by the return leakage metrics.\n"
            "4. Issue a formal Verification Scorecard with Mathematical Accuracy %, Hallucination Count, and Final Decision (APPROVED / REJECTED)."
        ),
        expected_output=(
            "A Verification Audit Scorecard certifying the mathematical accuracy, data grounding, and formal approval status of the report."
        ),
        agent=agents["verification_agent"],
        context=[task_strategy]
    )

    return [
        task_data_analysis,
        task_marketing,
        task_finance,
        task_operations,
        task_strategy,
        task_verification
    ]
