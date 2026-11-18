# Cloud Deployment Guide – Render & Vercel

**Document Reference:** DEP-GUIDE-2026-V1  
**Target Environments:**
- Backend & Managed PostgreSQL: **Render** (`https://render.com`)
- Frontend Single-Page App: **Vercel** (`https://vercel.com`)
- Source Control: **GitHub**

---

## 1. Architecture Deployment Overview

```mermaid
flowchart LR
    subgraph Vercel ["Frontend: Vercel"]
        V_App["React.js SPA (Vite Production Build)"]
    end

    subgraph Render ["Backend & Database: Render"]
        R_API["FastAPI Web Service (Python 3.13)"]
        R_DB["Managed PostgreSQL Database"]
    end

    V_App -->|HTTPS / REST API / Bearer Token| R_API
    R_API -->|SSL Connection Pool| R_DB
```

---

## 2. Part 1: Render PostgreSQL Database Setup

1. Log in to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** -> **PostgreSQL**.
3. Configure the database parameters:
   - **Name:** `retail-bi-db`
   - **Database:** `retail_bi`
   - **User:** `retail_admin`
   - **Region:** Frankfurt (EU Central) or Oregon (US West)
   - **Plan:** Free or Starter
4. Click **Create Database**.
5. Once provisioned, copy the **Internal Database URL** (for Render web service) or **External Database URL** (for remote admin tools):
   `postgresql://retail_admin:password@dpg-xxxxx.render.com/retail_bi`

---

## 3. Part 2: Render Backend Web Service Setup

1. Click **New +** -> **Web Service**.
2. Connect your GitHub repository containing the project.
3. Configure the Web Service settings:
   - **Name:** `retail-bi-backend`
   - **Runtime:** `Python 3`
   - **Build Command:**
     ```bash
     pip install -r requirements.txt && python backend/init_db.py
     ```
   - **Start Command:**
     ```bash
     uvicorn backend.main:app --host 0.0.0.0 --port $PORT
     ```
4. Configure Environment Variables in the Render Dashboard:
   | Key | Example Value | Description |
   | :--- | :--- | :--- |
   | `DATABASE_URL` | `postgresql://retail_admin:pass@dpg-xxx/retail_bi` | PostgreSQL connection string from Step 2 |
   | `SECRET_KEY` | `09d25e094faa6ca2556c818166b7a9563b...` | 64-character random hex string for JWT signing |
   | `GEMINI_API_KEY` | `AIzaSy...` | Your Google Gemini API Key |
   | `LLM_PROVIDER` | `gemini` | Primary LLM Provider |
   | `LLM_MODEL` | `gemini-1.5-flash` | Gemini model name |
5. Click **Create Web Service**.
6. Render will build dependencies, run `init_db.py` (which seeds the 6 retail sheets and creates default Admin and Manager users), and start Uvicorn.
7. Record the live backend URL: `https://retail-bi-backend.onrender.com`.

---

## 4. Part 3: Vercel Frontend Deployment

1. Log in to [Vercel Dashboard](https://vercel.com).
2. Click **Add New...** -> **Project**.
3. Import your GitHub repository.
4. Configure Project Settings:
   - **Framework Preset:** `Vite`
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
   - **Install Command:** `npm install`
5. Configure Environment Variables:
   | Key | Value | Description |
   | :--- | :--- | :--- |
   | `VITE_API_BASE_URL` | `https://retail-bi-backend.onrender.com/api/v1` | Live Render backend API URL |
6. Ensure `frontend/vercel.json` rewrite rule is in place for SPA routing:
   ```json
   {
     "rewrites": [
       { "source": "/(.*)", "destination": "/index.html" }
     ]
   }
   ```
7. Click **Deploy**. Vercel compiles the production bundle in under 30 seconds.
8. Record the live frontend URL: `https://retail-bi-frontend.vercel.app`.

---

## 5. Part 4: Post-Deployment Verification Checklist

- [ ] Open `https://retail-bi-backend.onrender.com/health` -> Returns `{"status":"healthy","database":"connected"}`.
- [ ] Open `https://retail-bi-backend.onrender.com/docs` -> Interactive Swagger UI loads with all 41 endpoints.
- [ ] Open Vercel frontend URL -> Sign in with `admin@retailbi.com` / `Admin@123456`.
- [ ] Verify Dashboard loads live numbers: `₹109,842,110.21` Net Revenue, `1,244` Orders, Recharts visualizations render.
- [ ] Navigate to `/analysis` and click **Execute Multi-Agent Analysis** -> Verify all 6 agents execute and logs populate.
- [ ] Navigate to `/chat` and ask *"What was my total revenue in September?"* -> Verify grounded answer.
- [ ] Navigate to `/approvals` -> Approve a proposal with manager notes -> Verify status update.
- [ ] Navigate to `/reports` -> Click **Download PDF** -> Verify generated vector PDF report.
