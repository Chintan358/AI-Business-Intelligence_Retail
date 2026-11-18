# Project Demonstration Script & Viva Defense Storyboard

**Project Name:** AI-Powered Smart Business Operations & Decision Intelligence System  
**Industry:** Retail – Sales & Inventory Operations  
**Evaluation Target:** Live Demonstration & Technical Viva (5 Marks)  

---

## 1. 5-Minute Demonstration Storyboard

| Step | Time | Screen / Module | Actions Performed | Key Talking Points for Evaluator |
| :---: | :---: | :--- | :--- | :--- |
| **1** | **0:00 - 0:45** | **Login & Authentication** | 1. Open app at `/login`.<br/>2. Click "Quick Demo - Admin Role".<br/>3. Sign in to executive dashboard. | • Secure password hashing using salted bcrypt.<br/>• JWT Bearer token authentication with RBAC (`admin`, `manager`, `analyst`).<br/>• Protected React routes. |
| **2** | **0:45 - 1:45** | **Executive Dashboard** | 1. Point to verified KPI cards.<br/>2. Review monthly trajectory chart.<br/>3. Review category mix & channel returns.<br/>4. Highlight the critical alert banner. | • Net Revenue: ₹109.84M across 1,244 completed orders.<br/>• Gross Profit: ₹24.19M (22.02% margin).<br/>• Negative operating profit (-₹3.92M) due to ₹28.11M OpEx.<br/>• Highlight the **50.24% order leakage**: 645 returns (₹54.54M lost) and 611 cancellations (₹51.35M lost).<br/>• Recharts visualizations are 100% grounded in live database queries. |
| **3** | **1:45 - 2:45** | **AI Multi-Agent Swarm** | 1. Navigate to `/analysis`.<br/>2. Click "Execute Multi-Agent Analysis".<br/>3. Watch live progress on `/agents/monitor`.<br/>4. Expand individual agent cards. | • Show real execution of **all six specialized agents**: Data Analyst, Marketing, Finance, Operations, Strategy, Verification.<br/>• Show upstream context passing into Strategy Agent.<br/>• Show the **Verification Agent audit scorecard** certifying 100% mathematical accuracy. |
| **4** | **2:45 - 3:30** | **Human-in-the-Loop Governance** | 1. Navigate to `/approvals`.<br/>2. Select pending strategic recommendation.<br/>3. Review expected ROI, risk level, and empirical evidence.<br/>4. Click "Approve Proposal", enter manager rationale, and submit. | • Explain the mandatory governance rule: AI agents are prohibited from executing consequential business actions autonomously.<br/>• Show decision, comments, and reviewer ID saved immutably in PostgreSQL audit log. |
| **5** | **3:30 - 4:15** | **Grounded AI Business Chat** | 1. Navigate to `/chat`.<br/>2. Click suggested chip: *"What was my total revenue in September?"*.<br/>3. Ask: *"Why did sales decrease?"*. | • Point out the green verification shield certifying zero hallucinations.<br/>• Explains the exact September dip (-14.01% to ₹17.56M) driven by warehouse stockouts in Grocery and Electronics.<br/>• Answers are grounded in database records. |
| **6** | **4:15 - 5:00** | **Reports & Conclusion** | 1. Navigate to `/reports`.<br/>2. Click "Download PDF".<br/>3. Open the downloaded PDF in viewer.<br/>4. Show Swagger `/docs` endpoint. | • Professional multi-page vector PDF report compiled with ReportLab.<br/>• Contains executive summary, KPI tables, monthly timeline, stockout hazards, and verification sign-off.<br/>• Summarize architecture: React + FastAPI + CrewAI + Gemini + PostgreSQL. |

---

## 2. Technical Viva Defense Q&A Preparation

### Q1: Why did you separate calculations from the LLM?
> **Answer:** LLMs are probabilistic sequence predictors and notoriously hallucinate arithmetic operations on large datasets. To ensure enterprise-grade accuracy, we built a deterministic `KPIService` using Pandas, NumPy, and SQL. The LLM only interprets verified findings and synthesizes strategic plans, while all numbers originate from ground truth calculations.

### Q2: How do your six CrewAI agents collaborate?
> **Answer:** We implemented a sequential-hierarchical pipeline. The **Data Analyst Agent** first computes the empirical baseline and monthly trends. Its structured output is passed via CrewAI context to the **Marketing**, **Finance**, and **Operations** agents, who analyze customer cohorts, store P&Ls, and warehouse stockouts simultaneously. Their consolidated findings feed into the **Strategy Agent**, which drafts the 90-day turnaround plan. Finally, the **Verification Agent** cross-checks every number against the database before signing off.

### Q3: What is your Human-in-the-Loop approval mechanism?
> **Answer:** Consequential actions like reallocating marketing budgets, altering return policies, or closing deficit stores are classified as high-risk. The Strategy Agent creates structured proposals in a `Pending` state. An authenticated manager must review the rationale, expected ROI, and risk disclosures, then submit an explicit approval or rejection with mandatory comments that are recorded in the PostgreSQL database.

### Q4: Why did net revenue drop in September 2026?
> **Answer:** Net revenue dropped from ₹20.42M in August to ₹17.56M in September (-14.01%). Our Operations and Data Analyst agents revealed that warehouses WH04 and WH06 depleted critical inventory in top Grocery and Electronics SKUs (e.g., PRD0085, PRD0192). Inability to fulfill customer orders coupled with cross-shipping delays between Gujarat and Maharashtra caused elevated cancellations before rebounding in October (+21.93%) after restocking.
