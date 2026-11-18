# System Architecture & Technical Design Specification

**Document Reference:** ARCH-RET-2026-V1  
**Project:** AI-Powered Smart Business Operations & Decision Intelligence System  
**Pattern:** Clean Layered Architecture with Autonomous Multi-Agent AI Subsystem  

---

## 1. High-Level Architecture Overview

```mermaid
flowchart TD
    subgraph ClientLayer ["Frontend Client Layer (React.js + Vite)"]
        UI_Dash["Executive BI Dashboard (Recharts)"]
        UI_Chat["Verified AI Business Assistant"]
        UI_Agents["Live Multi-Agent Execution Monitor"]
        UI_Approvals["Human-in-the-Loop Governance Panel"]
        UI_Upload["Dataset Upload & Preview Engine"]
        UI_Reports["PDF Report Download Hub"]
        UI_Admin["User & Admin Management"]
    end

    subgraph APILayer ["FastAPI Gateway & REST Layer"]
        AuthRouter["/api/v1/auth (JWT & RBAC)"]
        DatasetRouter["/api/v1/datasets (Excel/CSV Ingest)"]
        KPIRouter["/api/v1/kpis (Deterministic Calculations)"]
        AgentRouter["/api/v1/agents (CrewAI Orchestration)"]
        ChatRouter["/api/v1/chat (Tool-Grounded RAG)"]
        ApprovalRouter["/api/v1/approvals (HITL Workflow)"]
        ReportRouter["/api/v1/reports (ReportLab PDF Engine)"]
    end

    subgraph ServiceLayer ["Business Logic & Calculation Layer"]
        KPIService["Retail KPI Service (Pandas & NumPy)"]
        IngestService["Dataset Ingestion & Validation"]
        PDFService["ReportLab PDF Generator"]
        AuthService["Bcrypt & JWT Bearer Service"]
    end

    subgraph AgentLayer ["CrewAI Multi-Agent AI Subsystem"]
        A1["Agent 1: Data Analyst Agent"]
        A2["Agent 2: Marketing Agent"]
        A3["Agent 3: Finance Agent"]
        A4["Agent 4: Operations Agent"]
        A5["Agent 5: Strategy Agent"]
        A6["Agent 6: Verification Agent"]
        LLM["LLM Abstraction Layer (Gemini API)"]
    end

    subgraph DataLayer ["Data & Storage Layer (PostgreSQL)"]
        DB_Retail["Retail Tables (Customers, Products, Transactions, Items, Inventory, Expenses)"]
        DB_System["System Tables (Users, Profiles, Datasets, Sessions, Agent Logs, Approvals, Reports)"]
    end

    ClientLayer <-->|HTTPS / REST API / Bearer Token| APILayer
    APILayer --> ServiceLayer
    ServiceLayer <--> DataLayer
    APILayer --> AgentLayer
    AgentLayer -->|Deterministic Tools| KPIService
    AgentLayer --> LLM
    AgentLayer -->|Persist Logs & Outputs| DataLayer
```

---

## 2. Architectural Layers

### 2.1 Presentation Layer (React.js)
- **Framework:** React 18 with Vite build tooling.
- **Styling:** Tailwind CSS with responsive typography, dark/light slate enterprise color hierarchy.
- **Data Visualization:** Recharts (responsive area charts, bar charts, donut charts, and trend metrics).
- **State & Context:** React Context API (`AuthContext`) managing JWT session, active company profile, and persistent user preferences.
- **API Client:** Axios instance with request/response interceptors automatically injecting `Authorization: Bearer <token>` and handling token refresh/401 redirects.

### 2.2 API & Gateway Layer (Python FastAPI)
- **Routing:** Independent route modules under `backend/routers/` to ensure zero file bloat and high modularity.
- **Data Serialization:** Pydantic v2 schemas providing strict compile-time and runtime type validation for all incoming and outgoing payloads.
- **Security:** OAuth2 password bearer flow with HMAC-SHA256 JWT tokens. Role-based dependency checkers (`RoleChecker(['admin', 'manager'])`).
- **Background Execution:** FastAPI `BackgroundTasks` orchestrating long-running CrewAI multi-agent runs asynchronously while persisting status so the React frontend can poll or stream real-time progress.
- **OpenAPI / Swagger:** Interactive documentation automatically exposed at `/docs` and `/redoc`.

### 2.3 Business Logic & Calculation Layer
- **`KPIService`**: Centralized, reusable mathematical service using Pandas and NumPy. Dashboard metric endpoints, PDF report generators, and AI agent tools all consume this single source of truth.
- **`IngestionService`**: Handles file validation, reading multi-sheet Excel files with OpenPyXL, validating foreign key links, casting types, and executing atomic database transactions.
- **`PDFReportService`**: Built on ReportLab to generate publication-grade PDF documents with tabular layouts, KPI badges, executive summaries, and agent findings.

### 2.4 Multi-Agent Layer (CrewAI + LLM Provider Abstraction)
- **Framework:** CrewAI orchestrating 6 distinct agents.
- **LLM Abstraction:** A flexible provider wrapper (`LLMProvider`) designed to interface with Google Gemini (via `google-genai` / `crewai` LLM configuration) and capable of deterministic fallback if external network quotas are restricted.
- **Execution Workflow:** Sequential and hierarchical context delegation. Specialized agents analyze specific domains and forward structured outputs into the Strategy Agent. The Verification Agent performs mathematical cross-checking before marking any analysis session `Verified`.

### 2.5 Relational Persistence Layer (PostgreSQL)
- **Database Engine:** PostgreSQL (hosted on Render in production).
- **ORM:** SQLAlchemy 2.0 with connection pooling (`pool_size=10`, `max_overflow=20`), parameterized queries, and foreign key constraints.
- **Migrations:** Alembic ready for database versioning and schema maintenance.
