# backend/app/core/database.py
from sqlmodel import  create_engine, Session
from app.core.config import settings
import logging

# Configure logging (only show SQL if needed)
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(
    logging.INFO if settings.DEBUG else logging.WARNING)

# Create the database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,       # Show SQL only in debug mode
    pool_pre_ping=True,         # Check connections before using them
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,  
)


def get_session():
    """Dependency for FastAPI routes"""
    with Session(engine) as session:
        yield session


def get_db_session():
    """Manual session usage (outside of FastAPI DI)"""
    return Session(engine)


