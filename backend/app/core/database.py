# backend/app/core/database.py
from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings
import logging

# Set up logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,  # Set to False in production
    pool_pre_ping=True,  # Verify connections before use
)


def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)
    print("✅ Database tables created successfully!")


def get_session():
    """Get database session - use as dependency"""
    with Session(engine) as session:
        yield session

# For manual database operations


def get_db_session():
    """Get database session for manual operations"""
    return Session(engine)
