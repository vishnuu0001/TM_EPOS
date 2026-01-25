from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

# Get the backend directory path
BACKEND_DIR = Path(__file__).parent.parent
DATA_DIR = BACKEND_DIR / "data"

# Use Vercel writable temp directory when deployed
_IS_VERCEL = bool(os.getenv("VERCEL")) or bool(os.getenv("VERCEL_ENV"))
_DEFAULT_DB_URL = "sqlite:////tmp/epos.db" if _IS_VERCEL else f"sqlite:///{DATA_DIR}/epos.db"

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "ePOS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database - Use absolute path for SQLite
    DATABASE_URL: str = _DEFAULT_DB_URL
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "9xp5cNa3iTm2NgX/mmFcHeK3yXjRVhpDfyiR+SslNPM="
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8000"
    ]
    
    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "noreply@epos.com"
    
    # SMS Gateway
    SMS_API_URL: Optional[str] = None
    SMS_API_KEY: Optional[str] = None
    
    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".pdf", ".doc", ".docx"}
    
    # SAP Integration (Phase 1)
    SAP_API_URL: Optional[str] = None
    SAP_API_KEY: Optional[str] = None
    
    # Service URLs
    COLONY_SERVICE_URL: str = "http://localhost:8001"
    GUESTHOUSE_SERVICE_URL: str = "http://localhost:8002"
    EQUIPMENT_SERVICE_URL: str = "http://localhost:8003"
    VIGILANCE_SERVICE_URL: str = "http://localhost:8004"
    VEHICLE_SERVICE_URL: str = "http://localhost:8005"
    VISITOR_SERVICE_URL: str = "http://localhost:8006"
    CANTEEN_SERVICE_URL: str = "http://localhost:8007"
    
    class Config:
        env_file = str(BACKEND_DIR / ".env")
        case_sensitive = True


settings = Settings()
