import os
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from config import settings
from database import engine, Base
from routers import (
    auth, users, business, datasets, analytics, kpis,
    agents, analysis, chat, reports, approvals, admin
)

# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise Multi-Agent Business Intelligence & Decision Intelligence System for Retail Sales & Inventory Operations.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Configuration for React Frontend (Vercel & Local)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files Directory for Reports and Uploads
if os.path.exists(settings.STATIC_DIR):
    app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

# Include Modular API Routers
api_prefix = settings.API_V1_STR
app.include_router(auth.router, prefix=api_prefix)
app.include_router(users.router, prefix=api_prefix)
app.include_router(business.router, prefix=api_prefix)
app.include_router(datasets.router, prefix=api_prefix)
app.include_router(analytics.router, prefix=api_prefix)
app.include_router(kpis.router, prefix=api_prefix)
app.include_router(agents.router, prefix=api_prefix)
app.include_router(analysis.router, prefix=api_prefix)
app.include_router(chat.router, prefix=api_prefix)
app.include_router(reports.router, prefix=api_prefix)
app.include_router(approvals.router, prefix=api_prefix)
app.include_router(admin.router, prefix=api_prefix)

@app.get("/", tags=["Health"])
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "industry": "Retail – Sales & Inventory Operations",
        "status": "Healthy & Operational",
        "documentation": "/docs"
    }

@app.get("/health", tags=["Health"])
def healthcheck():
    return {
        "status": "healthy",
        "database": "connected",
        "multi_agent_system": "ready"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"An internal server error occurred: {str(exc)}"}
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
