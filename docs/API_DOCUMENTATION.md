# REST API Documentation & Endpoint Specification

**Base URL (Local):** `http://localhost:8000/api/v1`  
**Swagger Interactive Docs:** `http://localhost:8000/docs`  
**ReDoc Specification:** `http://localhost:8000/redoc`  
**Authentication:** Bearer Token (JWT in `Authorization: Bearer <token>` header)  

---

## 1. Authentication Endpoints (`/api/v1/auth`)

### 1.1 Register User
- **POST** `/auth/register`
- **Request Body:**
  ```json
  {
    "full_name": "Priya Sharma",
    "email": "priya.sharma@retailbi.com",
    "password": "Password@123",
    "role": "manager"
  }
  ```
- **Response (201 Created):**
  ```json
  {
    "id": 3,
    "email": "priya.sharma@retailbi.com",
    "full_name": "Priya Sharma",
    "role": "manager",
    "is_active": true,
    "created_at": "2026-11-18T14:00:00Z"
  }
  ```

### 1.2 User Login
- **POST** `/auth/login`
- **Form Data:** `username=<email>`, `password=<password>`
- **Response (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "role": "manager",
    "user_id": 3,
    "full_name": "Priya Sharma",
    "email": "priya.sharma@retailbi.com"
  }
  ```

### 1.3 Get Current User Profile
- **GET** `/auth/me`
- **Headers:** `Authorization: Bearer <token>`
- **Response (200 OK):** User object.

---

## 2. Business Profile Endpoints (`/api/v1/business`)

### 2.1 Get Business Profile
- **GET** `/business/profile`
- **Response (200 OK):**
  ```json
  {
    "id": 1,
    "user_id": 1,
    "company_name": "Apex Retail Global",
    "industry": "Retail",
    "team_size": "50-100",
    "target_margin": 25.0,
    "business_goals": "Drive gross profit margin to 25%, minimize digital return leakage, and eliminate stockouts on key inventory.",
    "updated_at": "2026-11-18T14:00:00Z"
  }
  ```

### 2.2 Update Business Profile
- **PUT** `/business/profile`
- **Request Body:** Partial JSON object of fields to update.

---

## 3. Deterministic KPI & Analytics Endpoints (`/api/v1/kpis`)

### 3.1 Get Executive Summary KPIs
- **GET** `/kpis/summary`
- **Response (200 OK):** Complete verified dictionary (Net Revenue, COGS, Gross Profit, Margins, OpEx, Net Profit, Order Completion Rate, etc.).

### 3.2 Get Monthly Trajectory
- **GET** `/kpis/monthly`
- **Response (200 OK):** Array of 6 months (May to October 2026) with MoM growth percentages and expense comparisons.

### 3.3 Get Merchandise Category Performance
- **GET** `/kpis/categories`
- **Response (200 OK):** Breakdown across Grocery, Electronics, Home, and Fashion.

### 3.4 Get Channel Performance
- **GET** `/kpis/channels`
- **Response (200 OK):** Orders, Net Revenue, Returns, Return Rate % for In-store, Online, and Mobile App.

### 3.5 Get Store P&L Performance
- **GET** `/kpis/stores`
- **Response (200 OK):** Array of 15 stores with Revenue, COGS, Allocated OpEx, and Net Profit.

### 3.6 Get Priority Stockout Alerts
- **GET** `/kpis/stockout-alerts?limit=15`
- **Response (200 OK):** Array of SKUs operating at or below safety reorder levels.

---

## 4. Multi-Agent Analysis Endpoints (`/api/v1/analysis`)

### 4.1 Start Analysis Session
- **POST** `/analysis/start`
- **Request Body:** `{"dataset_id": null}`
- **Response (200 OK):** Created `AnalysisSession` object with `status: "Pending"`. Background worker triggered.

### 4.2 List Analysis Sessions
- **GET** `/analysis/sessions`
- **Response (200 OK):** Array of all historical sessions sorted by newest first.

### 4.3 Get Session Details
- **GET** `/analysis/sessions/{session_id}`
- **Response (200 OK):** Detailed session object including `executive_summary`, `verification_scorecard`, and status.

### 4.4 Get Real-Time Agent Logs
- **GET** `/analysis/sessions/{session_id}/logs`
- **Response (200 OK):** Array of 6 agent log objects with status, start/end timestamps, execution duration, output text, and structured telemetry payload.

---

## 5. Human-in-the-Loop Approval Endpoints (`/api/v1/approvals`)

### 5.1 Get Pending Approvals
- **GET** `/approvals/pending`
- **Response (200 OK):** Array of requests with `decision: "Pending"`.

### 5.2 Get Complete Approval History
- **GET** `/approvals/all`
- **Response (200 OK):** Complete array of Pending, Approved, and Rejected requests.

### 5.3 Submit Manager Decision
- **POST** `/approvals/{request_id}/decision`
- **Request Body:**
  ```json
  {
    "decision": "Approved",
    "manager_comments": "Authorized for 60-day trial in Surat and Mumbai."
  }
  ```
- **Response (200 OK):** Updated approval request with recorded reviewer ID and decision timestamp.

---

## 6. Grounded AI Chat Assistant Endpoints (`/api/v1/chat`)

### 6.1 Submit Natural Language Query
- **POST** `/chat/query`
- **Request Body:**
  ```json
  {
    "query": "What was my total revenue in September?",
    "conversation_id": null
  }
  ```
- **Response (200 OK):** Factually grounded response with cross-referenced database figures.

---

## 7. Report Generation & Download Endpoints (`/api/v1/reports`)

### 7.1 List Generated Reports
- **GET** `/reports`
- **Response (200 OK):** Array of report records with title, size, and type.

### 7.2 Download Report PDF
- **GET** `/reports/{report_id}/download`
- **Response (200 OK):** Direct binary stream of the vector PDF file (`Content-Type: application/pdf`).

### 7.3 Instant On-Demand PDF Generation
- **POST** `/reports/generate-instant/{session_id}`
- **Response (200 OK):** Generates and registers a fresh PDF report in the database.
