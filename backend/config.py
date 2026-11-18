import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Powered Smart Business Operations & Decision Intelligence System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./retail_bi.db")
    
    # LLM Settings
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")  # gemini or mock
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-1.5-flash")
    
    # File Paths
    STATIC_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    REPORTS_DIR: str = os.path.join(STATIC_DIR, "reports")
    UPLOADS_DIR: str = os.path.join(STATIC_DIR, "uploads")
    DEFAULT_DATASET_PATH: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "03_Retail.xlsx"))

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

# Ensure directories exist
os.makedirs(settings.REPORTS_DIR, exist_ok=True)
os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
