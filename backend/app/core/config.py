# backend/app/core/config.py
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Database - will use Neon PostgreSQL or fallback to SQLite
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./learnhub.db")
    
    def __post_init__(self):
        db_type = "PostgreSQL" if self.DATABASE_URL.startswith(
            "postgresql") else "SQLite"
        print(f"📊 Using database: {db_type}")

    # JWT Settings
    JWT_SECRET: str = "your-super-secret-jwt-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000", "http://127.0.0.1:3000", "https://get-course-alpha.vercel.app/"]

    # App Settings
    APP_NAME: str = "LearnHub API"
    APP_VERSION: str = "1.0.0"

    # Debug mode (added for logging config and env flexibility)
    DEBUG: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
