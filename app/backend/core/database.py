"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings

# Create database engine
# Supabase provides a PostgreSQL connection string
if settings.DATABASE_URL:
    # Use connection pooling for better performance
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=5,
        max_overflow=10
    )
else:
    # Fallback - will raise error when trying to use
    engine = None

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    if SessionLocal is None:
        raise Exception("Database not configured. Set DATABASE_URL in environment variables.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

