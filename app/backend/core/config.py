"""
Application configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional, List
from pathlib import Path
import os

# Get project root (2 levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

# Default localhost origins for development
DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://frontend:3000",
]


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: Optional[str] = None
    SUPABASE_URL: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    
    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours for development/demo
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 30 days
    
    # CORS - Set via CORS_ORIGINS env var (comma-separated) for production
    # Example: CORS_ORIGINS=https://your-app.vercel.app,https://your-other-domain.com
    CORS_ORIGINS: str = ""  # Will be parsed in property
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS from env var or use defaults"""
        if self.CORS_ORIGINS:
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return DEFAULT_CORS_ORIGINS
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # MinIO/S3
    MINIO_ENDPOINT: Optional[str] = None
    MINIO_ACCESS_KEY: Optional[str] = None
    MINIO_SECRET_KEY: Optional[str] = None
    MINIO_BUCKET_NAME: str = "ehr-images"
    
    # AI Model Services
    VITAL_RISK_SERVICE_URL: str = "http://vital-risk-service:8001"
    IMAGE_ANALYSIS_SERVICE_URL: str = "http://image-analysis-service:8002"
    DIAGNOSIS_HELPER_SERVICE_URL: str = "http://diagnosis-helper-service:8003"
    
    class Config:
        env_file = str(ENV_FILE) if ENV_FILE.exists() else None
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env that aren't in the model


settings = Settings()

