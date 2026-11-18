# Enterprise User Manual & Operations Guide

**System:** AI-Powered Smart Business Operations & Decision Intelligence System  
**Industry:** Retail – Sales & Inventory Intelligence  

---

## 1. System Access & Authentication

### 1.1 First-Time Login
1. Navigate to the application URL.
2. Sign in using the pre-configured enterprise demonstration accounts:
   - **System Administrator:** `admin@retailbi.com` / `Admin@123456`
   - **Retail Business Manager:** `manager@retailbi.com` / `Manager@123456`
3. Click **Quick Demo Accounts** buttons for one-click credential pre-filling.

---

## 2. Navigating the 18 Screens

### Screen 1: Executive Operations Dashboard (`/`)
- **Key Metrics Grid**: Displays completed Net Revenue (₹109.84M), Gross Profit (₹24.19M), Operating Loss (-₹3.92M), and Completed Order Count (1,244).
- **Monthly Trajectory Chart**: Visualizes the revenue trajectory from May through October 2026, highlighting the September stockout dip and October peak.
- **Department Mix**: Compare sales and margin contributions across Grocery, Electronics, Home, and Fashion.
- **Omnichannel Fulfillment**: View completion vs return vs cancellation rates across In-store, Online, and Mobile App.
- **Stockout Alerts Table**: Direct alerts for products with stock below safety reorder levels.

### Screen 2: AI Business Analysis Hub (`/analysis`)
- Click **Execute Multi-Agent Analysis** to trigger the 6-agent CrewAI pipeline.
- View the active session status, execution time in seconds, and verified executive turnaround strategy.

### Screen 3: Live Agent Execution Monitoring (`/agents/monitor`)
- Track step-by-step progress as all six agents execute:
  1. Data Analyst Agent
  2. Marketing Agent
  3. Finance Agent
  4. Operations Agent
  5. Strategy Agent
  6. Verification Agent
- Expand any agent card to inspect its full reasoning text and structured telemetry payload.

### Screen 4: Grounded AI Business Assistant (`/chat`)
- Ask conversational retail questions grounded in database ground truth.
- Click any suggested chip (e.g., *"What was my total revenue in September?"*, *"Which products have inventory risks?"*, *"Why did sales decrease?"*).
- Answers include green verification badges certifying database grounding.

### Screen 5: Human-in-the-Loop Approval Center (`/approvals`)
- Review strategic turnaround proposals formulated by the Strategy Agent and certified by the Verification Agent.
- View expected ROI, risk level, and supporting evidence.
- Click **Approve Proposal** or **Reject** and submit mandatory manager rationale comments into the audit log.

### Screen 6: Reports & Downloads (`/reports`)
- Browse all compiled Business Intelligence reports.
- Click **Download PDF** to obtain publication-quality vector PDF reports with tables and verification certificates.
- Click **Generate On-Demand PDF** to compile fresh reports on demand.

### Screen 7: Report Details Viewer (`/reports/:id`)
- Deep in-browser preview of report metadata, executive strategy text, and audit certificates.

### Screen 8: Dataset Ingestion & Validation (`/datasets/upload`)
- Upload new `.xlsx`, `.xls`, or `.csv` files.
- The backend validates required sheets (`Customers`, `Products`, `Transactions`), executes schema checks, and updates the database.

### Screen 9: Dataset Record Preview (`/datasets/preview`)
- Switch tabs to inspect raw records from any of the 6 tables: Customers, Products, Transactions, Transaction Items, Inventory Movements, or Expenses.

### Screen 10: Dataset History (`/datasets/history`)
- Audit log of all ingested files, file sizes, and record counts.

### Screen 11: Business Profile & Goals (`/profile`)
- Update company name, team size, target gross margin percentage, and strategic quarterly goals.

### Screen 12: Admin Overview & Telemetry (`/admin`)
- Accessible to administrators only. Displays live database row counts and multi-agent execution counters.

### Screen 13: User Management (`/admin/users`)
- View registered users and modify user roles (`admin`, `manager`, `analyst`).

### Screen 14: System Settings (`/settings`)
- Configure Google Gemini API keys, select preferred LLM models, and review infrastructure status.
