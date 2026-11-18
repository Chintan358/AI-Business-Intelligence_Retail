# Project Requirement Analysis (PRA)

**Document Reference:** PRA-RET-2026-V1  
**Project:** AI-Powered Smart Business Operations & Decision Intelligence System  
**Industry:** Retail – Sales & Inventory Intelligence  
**Period Under Evaluation:** May 1, 2026 – October 31, 2026  
**Target Score:** 100 / 100 Marks  

---

## 1. Executive Summary & Objective

The objective of this project is to develop and deliver an industry-grade, enterprise-ready **AI-Powered Business Operations & Decision Intelligence Platform** specifically architected for the **Retail industry**. 

Unlike conventional chatbots, static dashboard templates, or simulated toy demonstrations, this platform integrates:
1. **Deterministic Data Processing**: Accurate, verifiable calculation of core retail metrics using Pandas, NumPy, and PostgreSQL.
2. **Six Autonomous CrewAI Agents**: Independent, specialized agents (Data Analyst, Marketing, Finance, Operations, Strategy, Verification) working in collaboration with clear task boundaries, context passing, and explicit reasoning.
3. **Verification & Anti-Hallucination Guardrails**: A dedicated Verification Agent that cross-checks LLM generated claims against mathematical source ground truth.
4. **Human-in-the-Loop (HITL) Governance**: Consequential business recommendations (e.g., budget reallocation, supplier negotiations, inventory orders) must be reviewed, approved, or rejected by authorized managers with audit trails.
5. **Modern Full-Stack SaaS Interface**: A responsive React.js SPA (Vite + Tailwind CSS + Recharts) powered by a clean, modular Python FastAPI REST backend.

---

## 2. Core Functional Requirements Breakdown

### Module A: Authentication & Security
- User registration and login with secure password hashing (`passlib`/`bcrypt`).
- JWT access tokens with expiration and Bearer authorization headers.
- Role-Based Access Control (RBAC): `admin`, `manager`, `analyst`.
- Protected frontend routes and API endpoints.

### Module B: Business Profile Management
- Configurable business parameters: Company name, retail segment, team size, primary business objectives (e.g., maximize margin, clear stagnant inventory), target metrics.
- Profile persisted in PostgreSQL and accessible by all AI agents as contextual background.

### Module C: Dataset Management & Ingestion
- Upload support for Excel (`.xlsx`) and CSV files.
- File integrity checks: schema validation, sheet verification, null handling, duplicate detection.
- Clean and normalize dataset into PostgreSQL tables.
- Dataset processing history, record counts, and error telemetry.

### Module D: Multi-Agent AI Business Analysis
- Trigger automated execution of 6 specialized CrewAI agents.
- Agent task delegation and structured context passing:
  `Data Analyst -> Marketing & Finance & Operations -> Strategy -> Verification`.
- Live execution tracking (Agent name, task status, execution duration, reasoning output).
- Consolidated Business Intelligence output saved with versioned session IDs.

### Module E: Verified AI Chat Interface
- Natural language query interface allowing executives to ask business questions:
  - *"What was my total net revenue in September 2026?"*
  - *"Which product categories generated the highest gross margin?"*
  - *"Which products have immediate stockout risks based on reorder levels?"*
  - *"Why did sales dip in September relative to August?"*
- Answers strictly grounded in SQL queries and deterministic KPI engine outputs; no fabricated metrics.

### Module F: Analytics Dashboard
- Executive KPI summary cards (Total Revenue, Orders, COGS, Gross Profit, Gross Margin %, Average Order Value, Customer Count, Stagnant Inventory).
- Recharts visualizations:
  - Monthly Revenue & Gross Profit Trends (May - Oct 2026)
  - Category-wise Sales & Profitability Breakdown
  - Store-wise Performance and Channel Distribution (In-store vs Online vs Mobile App)
  - Order Status distribution (Completed vs Cancelled vs Returned)
  - Inventory Reorder Alerts & Stock Velocity
- Automated business alerts generated from deterministic thresholds.

### Module G: Human-in-the-Loop Approval Workflow
- When Strategy Agent generates consequential strategic recommendations (e.g., *"Reallocate 15% of marketing budget from Card channel promotions to Surat store localized campaigns"*):
  1. Strategy Agent drafts recommendation with rationale and expected ROI.
  2. Verification Agent checks supporting evidence.
  3. System creates a `Pending` approval request in PostgreSQL.
  4. Manager views proposal, supporting data, and risk factors.
  5. Manager submits action: `Approve` or `Reject` with audit notes.
  6. Action status is persisted in the database.

### Module H: PDF Report Generation
- Professional downloadable PDF reports formatted using ReportLab:
  1. Consolidated Master Business Intelligence Report.
  2. 6 Specialist Agent Reports (Data Analysis, Marketing, Finance, Operations, Strategy, Verification).
- Standardized formatting: Header, Company metadata, KPI summaries, structured tables, visual indicators, and timestamped sign-offs.

### Module I: Admin & Session Management
- User management and role assignment.
- Historical analysis session retrieval and KPI snapshot comparison.
- Full agent execution log viewer.

---

## 3. Technology Stack Alignment

| Layer | Requirement | Chosen Implementation | Justification |
| :--- | :--- | :--- | :--- |
| **Frontend** | React.js, Vite, Tailwind CSS, Recharts, Axios, React Router | React 18, Vite 5, Tailwind CSS 3, Lucide React, Recharts | Fast HMR, responsive enterprise styling, rich data visualization |
| **Backend** | Python, FastAPI, SQLAlchemy, Pydantic | Python 3.13 / FastAPI, SQLAlchemy 2.0, Pydantic v2 | High-performance async REST APIs, automatic OpenAPI/Swagger generation |
| **Multi-Agent AI** | CrewAI + Gemini LLM | CrewAI 0.86+, Google Gemini 1.5 Flash / Pro (with LLM abstraction layer) | Multi-agent coordination with role-based backstories and pluggable LLM interfaces |
| **Database** | PostgreSQL | PostgreSQL (compatible with Render live deployment & local SQLite fallback for isolated tests) | Production-grade relational storage with foreign keys, indexes, and transactions |
| **Data Engine** | Pandas, NumPy, OpenPyXL | Pandas 2.2+, NumPy, OpenPyXL | Deterministic KPI calculation layer; eliminates LLM calculation errors |
| **Reporting** | Downloadable PDF | ReportLab 4.x | Pixel-perfect vector PDF generation with tables and charts |
| **Deployment** | Vercel (FE), Render (BE & DB) | GitHub Actions ready, Render Web Service & Render Managed PostgreSQL, Vercel SPA | Cloud production deployment with automated CI/CD and secure environment configuration |

---

## 4. Constraints & Non-Functional Requirements

1. **Deterministic Accuracy**: The LLM is never relied upon to add, multiply, or compute business metrics. All numerical values must flow through the shared Python KPI Service.
2. **Zero Fabrication**: Any metric not supported by the dataset (e.g., customer acquisition cost or ad impressions) must be explicitly noted as a dataset boundary rather than hallucinated.
3. **Data Period Boundary**: Analysis strictly spans May 1, 2026 through October 31, 2026.
4. **Security & Secrets**: No API keys, passwords, or tokens hardcoded or committed to git.
