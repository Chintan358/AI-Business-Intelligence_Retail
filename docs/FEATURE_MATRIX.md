# Feature Matrix & Capability Mapping

**Document Reference:** FM-RET-2026-V1  
**Project:** AI-Powered Smart Business Operations & Decision Intelligence System  
**Industry:** Retail – Sales & Inventory Intelligence  

---

## 1. Feature Matrix by Module

| Module | Feature | Mandatory Requirement | Implementation Strategy | Status |
| :--- | :--- | :---: | :--- | :---: |
| **Authentication** | User Registration | Yes | FastAPI `/auth/register` with bcrypt hash & email uniqueness check | Planned |
| | User Login | Yes | FastAPI `/auth/login` returning signed JWT Bearer token | Planned |
| | Token Refresh / Expiry | Yes | Expirable JWT with token refresh endpoint | Planned |
| | Role-Based Access Control | Yes | FastApi Depends with `RoleChecker(['admin', 'manager'])` | Planned |
| | Protected Frontend Routing | Yes | React Router `<ProtectedRoute>` checking token in localStorage | Planned |
| **Business Profile** | Company Profile Setup | Yes | Store Name, Industry, Segment, Target Margin, Objectives in DB | Planned |
| | Profile Update & Edit | Yes | REST endpoint `/business/profile` (GET/PUT) | Planned |
| **Dataset Management** | Excel & CSV Upload | Yes | Multi-part form upload with MIME & extension validation | Planned |
| | File Validation & Error Check | Yes | Check sheet names, non-empty, schema headers, date ranges | Planned |
| | Data Cleaning & Normalization | Yes | Cast dtypes, strip strings, handle nulls, verify FKs | Planned |
| | Ingestion into Database | Yes | Bulk insert into PostgreSQL via SQLAlchemy Core / ORM | Planned |
| | Upload History & Logs | Yes | Audit log of upload files, row counts, user IDs, timestamps | Planned |
| **KPI Engine** | Deterministic Retail Metrics | Yes | Pure Python/Pandas/SQL service layer; no LLM calculations | Planned |
| | Revenue & COGS Calculations | Yes | Net Revenue = Gross - Discount; COGS = Qty * Unit Cost | Planned |
| | Margin & Profit Breakdown | Yes | Gross Profit, Gross Margin %, OpEx, Operating Profit | Planned |
| | Monthly Comparisons | Yes | MoM percentage growth across May–October 2026 | Planned |
| | Channel & Store Performance | Yes | Distribution across In-store, Online, Mobile App & 15 Stores | Planned |
| **CrewAI Multi-Agent** | Data Analyst Agent | Yes | Retail KPI calculation, monthly anomaly detection, patterns | Planned |
| | Marketing Agent | Yes | Customer segmentation, repeat purchase analysis, retention | Planned |
| | Finance Agent | Yes | Revenue, OpEx, profit margins, cost optimization | Planned |
| | Operations Agent | Yes | Inventory stockout alerts, warehouse velocity, transfer waste | Planned |
| | Strategy Agent | Yes | Consolidated business improvement plan & recommendations | Planned |
| | Verification Agent | Yes | Numerical cross-check, hallucination detection, sign-off | Planned |
| | Sequential / Hierarchical Flow | Yes | CrewAI pipeline: Analyst -> Specialists -> Strategy -> Verify | Planned |
| | Agent Execution Monitoring | Yes | Real-time status display on frontend (running, done, output) | Planned |
| **AI Chat Assistant** | Grounded Natural Language Q&A | Yes | LangChain/CrewAI tools connected to DB SQL & KPI engine | Planned |
| | Anti-Hallucination Guardrail | Yes | System prompt enforces strictly verified DB figures | Planned |
| | Suggested Retail Queries | Yes | Preset quick prompt chips for common business questions | Planned |
| **Human-in-the-Loop** | Recommendation Proposal | Yes | Strategy Agent creates structured actionable proposals | Planned |
| | Manager Review & Decisions | Yes | Manager UI to view rationale, risk, ROI, and Approve/Reject | Planned |
| | Audit Trail | Yes | Persist approver ID, timestamp, decision, and comments in DB | Planned |
| **Dashboard & Viz** | Executive KPI Cards | Yes | Revenue, Orders, COGS, Profit, Margin %, AOV, Stock Alerts | Planned |
| | Monthly Trend Charts | Yes | Recharts Area/Bar charts for Revenue vs Expenses May-Oct | Planned |
| | Category & Channel Viz | Yes | Recharts Pie/Donut & Bar charts for department mix | Planned |
| | Interactive Filters | Yes | Filter by month, store, channel, order status | Planned |
| **Report Generation** | Master Consolidated BI PDF | Yes | ReportLab downloadable PDF with executive summary & charts | Planned |
| | 6 Individual Specialist PDFs | Yes | Downloadable PDF reports for each individual agent output | Planned |
| | Historical Report Archive | Yes | Download previously generated reports from database history | Planned |
| **Admin Dashboard** | User Management | Yes | View, activate, deactivate users and assign roles | Planned |
| | System Telemetry | Yes | Database record counts, agent execution counts, API metrics | Planned |
| **Deployment** | Backend Deployment | Yes | Render Web Service with healthcheck & Alembic migrations | Planned |
| | Database Deployment | Yes | Render Managed PostgreSQL live connection | Planned |
| | Frontend Deployment | Yes | Vercel SPA deployment with rewrite routing rules | Planned |
| | Source Control | Yes | GitHub repository with clean commits and documentation | Planned |
