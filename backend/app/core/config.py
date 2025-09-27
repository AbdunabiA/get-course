# backend/app/core/config.py
from pydantic_settings import BaseSettings
from typing import List, Union
from pydantic import validator
import os


class Settings(BaseSettings):
    # Database - Neon PostgreSQL or fallback to SQLite
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./learnhub.db")

    def __post_init__(self):
        db_type = "PostgreSQL" if self.DATABASE_URL.startswith(
            "postgresql") else "SQLite"
        print(f"📊 Using database: {db_type}")

    # JWT Settings
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-this-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS Settings
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:3000", "https://get-course-alpha.vercel.app"]

    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    # App Settings
    APP_NAME: str = "LearnHub API"
    APP_VERSION: str = "1.0.0"

    # Debug mode
    DEBUG: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
