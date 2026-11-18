# Local Project Setup & Development Guide

**Project:** AI-Powered Smart Business Operations & Decision Intelligence System  
**Prerequisites:** Python 3.10+ & Node.js 18+  

---

## 1. Quick Start in 3 Steps

### Step 1: Clone & Configure Backend
```bash
# Clone the repository
git clone <your-repo-url>
cd Multiagent

# Create Python virtual environment (optional but recommended)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install backend dependencies
pip install -r requirements.txt

# Initialize database tables and seed sample retail dataset
python backend/init_db.py
```

### Step 2: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Populate `.env` with your settings (SQLite is enabled by default for zero-setup local dev; PostgreSQL for production):
```ini
DATABASE_URL=sqlite:///./retail_bi.db
SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
GEMINI_API_KEY=your_gemini_api_key_here
LLM_PROVIDER=gemini
LLM_MODEL=gemini-1.5-flash
```

### Step 3: Run Backend & Frontend

#### Terminal 1 – Start FastAPI Server:
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be live at `http://127.0.0.1:8000/docs`.

#### Terminal 2 – Start React Frontend:
```bash
cd frontend
npm install
npm run dev
```
The React SPA will be live at `http://localhost:3000`.

---

## 2. Default Login Credentials

| Role | Email | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **System Admin** | `admin@retailbi.com` | `Admin@123456` | Full system access, User role management, Admin telemetry |
| **Retail Manager** | `manager@retailbi.com` | `Manager@123456` | Dashboard, Analysis, Approvals, Chat, Reports, Uploads |

---

## 3. Running Automated Tests
```bash
python -m pytest tests/
```
All 12 automated unit and integration tests will execute and pass.
