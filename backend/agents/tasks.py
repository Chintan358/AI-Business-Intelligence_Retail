"""
CrewAI task definitions.

Design rules
------------
* No business figure is written into a prompt. Agents must obtain every number
  from their tools (which read the database through KPIService).
* The four analyst tasks are chained with `context=[...]`, so each agent
  receives the previous agents' outputs. The Strategy task receives all four.
* The Strategy task must return strict JSON so recommendations can be validated
  and routed to the human-approval workflow.
"""
import json
from typing import Dict, List

from crewai import Task

GROUNDING_RULES = (
    "GROUNDING RULES (mandatory):\n"
    "- Call your tools first. Use ONLY figures returned by tools.\n"
    "- Never estimate, round creatively, or invent a figure. If a figure is not in a "
    "tool result, say it is unavailable.\n"
    "- If you derive a number (a share, a difference), show the formula and the inputs.\n"
    "- Quote rupee values and percentages exactly as the tools return them.\n"
)


def create_tasks(agents: dict, kpi_metric_keys: List[str]) -> List[Task]:
    """Returns the five sequential analysis/strategy tasks (verification runs after)."""

    task_data_analysis = Task(
        description=(
            "Analyse the May 1 - October 31, 2026 retail dataset.\n"
            "1. Call get_executive_kpis and get_monthly_sales_trend.\n"
            "2. Report net revenue, gross profit and margin, completed orders, AOV and units sold.\n"
            "3. Describe the month-by-month trajectory. For every month with a notable change "
            "(growth or decline), quote the MoM % from the tool and state ONLY drivers you can "
            "support with tool data; mark any explanation you cannot support as 'hypothesis'.\n"
            "4. Call get_category_performance and get_channel_performance and compare departments "
            "and channels.\n"
            "5. List anomalies (unusual month changes, unusually high return/cancellation rates).\n\n"
            + GROUNDING_RULES
        ),
        expected_output=(
            "Analytical Findings Report: KPI summary, monthly trend table with MoM %, category and "
            "channel comparison, and a list of anomalies. All figures taken from tool output."
        ),
        agent=agents["data_analyst"],
    )

    task_marketing = Task(
        description=(
            "Using the Data Analyst's findings (in your context) and your own tool calls:\n"
            "1. Call get_customer_segments and get_channel_performance.\n"
            "2. Compare the customer segments on customers, orders, revenue, AOV and revenue share.\n"
            "3. Report the repeat purchase rate and active customers exactly as get_executive_kpis "
            "/ the Data Analyst report state them.\n"
            "4. Compare channels on return and cancellation behaviour. Do NOT claim any channel "
            "is worse unless the tool figures show it.\n"
            "5. Recommend retention and growth actions, each tied to a figure you retrieved.\n\n"
            + GROUNDING_RULES
        ),
        expected_output=(
            "Marketing & Customer Intelligence Report: segment comparison, repeat-purchase "
            "analysis, channel behaviour comparison, growth opportunities and retention actions."
        ),
        agent=agents["marketing_agent"],
        context=[task_data_analysis],
    )

    task_finance = Task(
        description=(
            "Using the Data Analyst's findings (in your context) and your own tool calls:\n"
            "1. Call get_executive_kpis, get_category_performance and get_store_pnl_performance.\n"
            "2. Report revenue, COGS, gross profit and margin, operating expenses and operating "
            "profit/loss.\n"
            "3. Identify the stores and categories with the weakest profitability, using the "
            "store P&L figures only.\n"
            "4. Identify financial risks and quantify them with tool figures.\n"
            "5. Recommend cost-optimisation actions with the specific tool figure each is based on.\n\n"
            + GROUNDING_RULES
        ),
        expected_output=(
            "Financial Intelligence Report: P&L summary, expense drivers, weakest stores/categories, "
            "financial risks and cost-optimisation recommendations."
        ),
        agent=agents["finance_agent"],
        context=[task_data_analysis],
    )

    task_operations = Task(
        description=(
            "Using the Data Analyst's findings (in your context) and your own tool calls:\n"
            "1. Call get_stockout_risks and get_top_and_slow_products.\n"
            "2. List the SKUs at or below reorder level, with current stock, reorder level and "
            "deficit exactly as returned.\n"
            "3. Identify slow-moving and top-selling products.\n"
            "4. Identify operational bottlenecks that the tool data supports, and propose process "
            "improvements.\n\n"
            + GROUNDING_RULES
        ),
        expected_output=(
            "Operations & Supply Chain Report: stockout hazards, product velocity, bottlenecks "
            "and process-improvement recommendations."
        ),
        agent=agents["operations_agent"],
        context=[task_data_analysis],
    )

    schema = {
        "executive_summary": "string, max 150 words",
        "growth_opportunities": ["string"],
        "business_risks": ["string"],
        "improvement_plan": [
            {"phase": "Days 1-30", "actions": ["string"], "owner": "string"}
        ],
        "recommendations": [
            {
                "title": "string",
                "category": "Marketing | Finance | Operations | Strategy",
                "description": "string",
                "expected_roi": "string, qualitative or clearly labelled as an estimate",
                "risk_level": "Low | Medium | High",
                "evidence_metrics": {"<metric_key>": "<number copied exactly from get_executive_kpis>"},
            }
        ],
        "contradictions_resolved": ["string"],
    }
    task_strategy = Task(
        description=(
            "You have received the reports of the Data Analyst, Marketing, Finance and Operations "
            "agents in your context.\n"
            "1. Combine them into one business-improvement strategy. Where two reports disagree, "
            "resolve it using get_executive_kpis and list it in contradictions_resolved.\n"
            "2. Identify growth opportunities and business risks.\n"
            "3. Build a 90-day improvement plan (phases with actions and owners).\n"
            "4. Produce 3 to 6 consequential recommendations. Each one needs 'evidence_metrics': "
            "a JSON object mapping a metric key to the number copied EXACTLY from "
            "get_executive_kpis. Allowed keys: " + ", ".join(kpi_metric_keys) + ".\n"
            "   Targets and projections are allowed in descriptions but must be labelled "
            "'target' or 'estimate'. Every recommendation will be sent to a human manager for "
            "approval; do not phrase any as already approved or executed.\n\n"
            "Return ONLY one valid JSON object, no markdown, matching this shape:\n"
            + json.dumps(schema, indent=2) + "\n\n" + GROUNDING_RULES
        ),
        expected_output="A single valid JSON object following the schema above.",
        agent=agents["strategy_agent"],
        context=[task_data_analysis, task_marketing, task_finance, task_operations],
    )

    return [task_data_analysis, task_marketing, task_finance, task_operations, task_strategy]


def create_verification_task(agent, strategy_json: str, audit_summary: dict) -> Task:
    """Verification Agent review of the final strategy plus the deterministic audit."""
    schema = {
        "verdict": "APPROVED | REJECTED",
        "confidence": "High | Medium | Low",
        "unsupported_claims": ["string"],
        "contradictions": ["string"],
        "low_confidence_findings": ["string"],
        "rationale": "string",
    }
    return Task(
        description=(
            "You are the final gate before a report reaches a human manager.\n\n"
            "INPUT 1 - consolidated strategy (JSON):\n" + strategy_json + "\n\n"
            "INPUT 2 - result of the automated numeric audit of the analyst reports "
            "(every number was compared with database values):\n"
            + json.dumps(audit_summary, indent=2, default=str) + "\n\n"
            "Do the following:\n"
            "1. Call get_executive_kpis and use verify_metric_calculation on at least three "
            "figures that the strategy relies on.\n"
            "2. List any statement that is not supported by data (unsupported_claims).\n"
            "3. Detect recommendations that contradict each other (contradictions).\n"
            "4. Flag findings you consider low confidence (low_confidence_findings).\n"
            "5. REJECT if the audit shows unverified figures that the strategy depends on, if any "
            "recommendation lacks evidence, or if recommendations contradict each other. "
            "Otherwise APPROVE.\n\n"
            "Return ONLY one valid JSON object, no markdown, in this shape:\n"
            + json.dumps(schema, indent=2)
        ),
        expected_output="A single valid JSON object following the schema above.",
        agent=agent,
    )


def create_correction_task(agent, original_report: str, flagged_claims: List[dict]) -> Task:
    """Sends a report back to its author with the specific unverified numbers."""
    flagged = [
        {"claim": c["claim"], "sentence": c["context"], "closest_database_value": c["ground_truth"]}
        for c in flagged_claims[:25]
    ]
    return Task(
        description=(
            "The Verification layer compared your previous report with the database and found "
            "numbers it could not verify.\n\nUNVERIFIED NUMBERS:\n"
            + json.dumps(flagged, indent=2, default=str) + "\n\n"
            "YOUR PREVIOUS REPORT:\n" + original_report + "\n\n"
            "Re-query your tools, then rewrite the COMPLETE report. Replace each unverified "
            "number with the exact tool value, or remove the statement if no tool supports it.\n\n"
            + GROUNDING_RULES
        ),
        expected_output="The complete corrected report, with every figure taken from tool output.",
        agent=agent,
    )


def create_strategy_revision_task(
    agent, reports: Dict[str, str], issues: List[str], kpi_metric_keys: List[str]
) -> Task:
    """Strategy Agent re-run after corrections or invalid evidence."""
    return Task(
        description=(
            "Your previous strategy failed verification.\n\nISSUES:\n- "
            + "\n- ".join(issues or ["Underlying reports were corrected."]) + "\n\n"
            "CORRECTED SPECIALIST REPORTS:\n"
            + "\n\n".join(f"### {k}\n{v}" for k, v in reports.items()) + "\n\n"
            "Rebuild the strategy as ONE valid JSON object with the same fields as before "
            "(executive_summary, growth_opportunities, business_risks, improvement_plan, "
            "recommendations with evidence_metrics, contradictions_resolved). evidence_metrics "
            "keys must come from: " + ", ".join(kpi_metric_keys) + ", with values copied exactly "
            "from get_executive_kpis. Return ONLY the JSON object.\n\n" + GROUNDING_RULES
        ),
        expected_output="A single valid JSON object.",
        agent=agent,
    )
