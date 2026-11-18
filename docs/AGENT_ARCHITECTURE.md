# Six Specialized CrewAI Agents Architecture

**Document Reference:** AGT-ARCH-2026-V1  
**Framework:** CrewAI + Large Language Model (Gemini / Configurable Abstraction)  
**Industry:** Retail – Sales & Inventory Operations  

---

## 1. Multi-Agent Design Philosophy

1. **Strict Specialization**: No generic agents. Each agent possesses a tailored role, concise goal, distinct professional backstory, domain-specific tasks, and dedicated tools.
2. **Deterministic Tool Grounding**: When an agent requires financial figures, retention rates, or inventory valuations, it invokes tools connecting to the deterministic Python `KPIService`. The LLM's role is analytical reasoning, pattern interpretation, and strategic synthesis—never arithmetic calculation.
3. **Information Chaining**: Downstream agents receive structured outputs from upstream agents via CrewAI's `context=[task1, task2, ...]` dependency graph.
4. **Independent Verification**: A designated Verification Agent acts as an adversarial auditor, reviewing all factual and numerical statements before report publication.

---

## 2. Agent Profiles & Specifications

```mermaid
flowchart LR
    A1["1. Data Analyst Agent<br/>(Metrics & Anomalies)"] --> A2["2. Marketing Agent<br/>(Customer & Retention)"]
    A1 --> A3["3. Finance Agent<br/>(P&L & OpEx)"]
    A1 --> A4["4. Operations Agent<br/>(Inventory & Logistics)"]
    A2 & A3 & A4 --> A5["5. Strategy Agent<br/>(Consolidation & Action Plan)"]
    A5 --> A6["6. Verification Agent<br/>(Audit & Guardrails)"]
    A6 -->|Approved| Live["Verified BI Report"]
    A6 -->|Rejected| A5
```

---

### Agent 1: Data Analyst Agent
- **Role:** Principal Retail Data Scientist & KPI Specialist
- **Goal:** Analyze multi-store transaction datasets, compute deterministic retail KPIs, identify monthly trends (May–October 2026), detect anomalies, and establish empirical baselines.
- **Backstory:**
  > "You are a seasoned retail data scientist with 15 years of experience analyzing enterprise point-of-sale systems, basket transactions, and customer purchase histories. You hold an uncompromising standard for numerical rigor: you never guess figures, compute metrics strictly from raw data, and identify hidden variance patterns across sales channels, cities, and product categories."
- **Tools:** `get_dataset_kpis_tool`, `get_monthly_sales_trend_tool`, `get_category_performance_tool`, `get_channel_breakdown_tool`.
- **Primary Outputs:**
  - Complete KPI summary (Gross Revenue, Net Revenue, Discounts, Completed Orders, AOV, Units Sold).
  - Monthly MoM variance timeline (May to October 2026).
  - Diagnosis of the September revenue dip (-14.0%) and October rebound (+21.9%).
  - Channel volume and fulfillment breakdown.

---

### Agent 2: Marketing Agent
- **Role:** Chief Retail Marketing Strategist & Customer Intelligence Director
- **Goal:** Segment customer cohorts, evaluate retention and repeat purchase behavior, assess channel return rates, and recommend targeted loyalty and promotional strategies.
- **Backstory:**
  > "You are an elite retail marketing executive specializing in customer lifetime value (LTV), cohort retention, and omnichannel engagement. You analyze customer purchasing frequency across Regular, New, Wholesale, and Premium tiers. You understand that uncalibrated discounts destroy margins and high return rates on digital channels signify misaligned promotional messaging."
- **Tools:** `get_customer_segmentation_tool`, `get_repeat_purchase_metrics_tool`, `get_channel_returns_tool`.
- **Primary Outputs:**
  - Segment profile (Wholesale & Premium vs Regular & New).
  - Repeat purchase analysis (341 repeat buyers out of 739 active completed customers = 46.14%).
  - Investigation into digital channel return leakage (Online & Mobile App return rates vs In-store).
  - Targeted marketing recommendations (e.g., dedicated Wholesale account managers in Surat and Mumbai; revision of return incentives).

---

### Agent 3: Finance Agent
- **Role:** Corporate Retail Financial Controller & Cost Optimization Officer
- **Goal:** Analyze gross margin, Cost of Goods Sold (COGS), operating expenses by store and category, identify financial burn rates, and recommend cash flow and margin enhancements.
- **Backstory:**
  > "You are a former Big Four senior financial auditor and retail CFO. You look past top-line revenue to examine gross margin percentage, supplier acquisition costs, and operating overheads. You know that high sales volume with a negative net operating margin means structural insolvency. You demand strict cost control and contribution margin discipline across all 15 retail stores."
- **Tools:** `get_financial_pl_tool`, `get_store_expenses_breakdown_tool`, `get_low_margin_products_tool`.
- **Primary Outputs:**
  - Gross Profit (₹24.19M on ₹109.84M Net Revenue = 22.02% Gross Margin).
  - Operating Expense breakdown by category (Marketing: ₹5.32M, Rent: ₹5.23M, Salaries: ₹4.81M, Logistics: ₹4.45M, Packaging: ₹4.38M, Utilities: ₹3.91M).
  - Net Operating Deficit analysis (-₹3.92M) and store-level P&L identification (isolating stores `STR03`, `STR09`, `STR13`).
  - Actionable cost reduction targets to achieve positive operating margin.

---

### Agent 4: Operations Agent
- **Role:** VP of Retail Supply Chain & Warehouse Logistics
- **Goal:** Audit multi-warehouse inventory velocity, identify stockout hazards against reorder levels, evaluate stock transfer waste, and optimize replenishment schedules.
- **Backstory:**
  > "You are a global supply chain director with deep operational expertise in warehouse inventory turns, safety stocks, lead-time variance, and logistics fulfillment. You prevent stockouts of best-selling products while eliminating holding costs on slow-moving inventory across regional distribution centers."
- **Tools:** `get_inventory_health_tool`, `get_stockout_risks_tool`, `get_warehouse_movement_tool`.
- **Primary Outputs:**
  - Warehouse distribution analysis across 8 regional centers (`WH01` - `WH08`).
  - Catalog-wide stock balance and low-stock product identification (`stock <= reorder_level`).
  - Evaluation of 1,800 inventory movements (Adjustments, Returns, Purchases, Transfers, Sales).
  - Warehouse efficiency recommendations: localized fulfillment in Gujarat hubs to curb inter-state shipping overhead.

---

### Agent 5: Strategy Agent
- **Role:** Principal Management Consultant & Turnaround Strategist
- **Goal:** Synthesize domain findings from Data Analyst, Marketing, Finance, and Operations agents into an actionable, prioritized 90-day turnaround plan with projected ROI and risk analysis.
- **Backstory:**
  > "You are a senior partner at a tier-1 strategy consulting firm specializing in retail transformations. You excel at synthesizing conflicting operational realities into a coherent executive roadmap. You balance growth against financial solvency, prioritize high-impact initiatives, and formulate clear, measurable recommendations for executive approval."
- **Tools:** Consumes context from Agents 1, 2, 3, and 4.
- **Primary Outputs:**
  - Consolidated Executive Summary.
  - Prioritized Strategic Recommendations (P1: High Impact/Urgent to P4: Long-term).
  - Quantified Turnaround Plan (expected cost savings, margin uplift, and timeline).
  - Formal managerial approval requests with explicit rationale and risk disclosures.

---

### Agent 6: Verification Agent
- **Role:** Chief Compliance Auditor & Mathematical Verification Inspector
- **Goal:** Audit the final strategic report, cross-check every stated numerical value against database ground truth, detect logical inconsistencies or hallucinations, and formally approve or reject the publication.
- **Backstory:**
  > "You are an independent quality assurance auditor and mathematical verification officer. Your sole responsibility is ensuring that no ungrounded claims, hallucinated figures, or contradictory strategies enter the board report. If an agent claims ₹120M revenue when source data proves ₹109.84M, or recommends expanding budget in a bankrupt store, you flag the defect and reject the report."
- **Tools:** `verify_metric_grounding_tool`, `audit_report_consistency_tool`.
- **Primary Outputs:**
  - Verification Scorecard (Mathematical accuracy %, Hallucination count, Consistency rating).
  - Line-by-line audit trail matching claims to verified database formulas.
  - Final verdict: `APPROVED` (Report certified for executive presentation) or `REJECTED` (returned for correction).
