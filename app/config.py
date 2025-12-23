# app/config.py
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # App Info
    APP_NAME: str = "AI Content Detector API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # API
    API_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: str = "*"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # API Keys
    API_KEYS: str = '[]'  # JSON string of API keys

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
