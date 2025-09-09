from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create database engine with appropriate configuration
# SQLite requires check_same_thread=False, PostgreSQL doesn't need it
if settings.database_url.startswith("sqlite"):
    # SQLite configuration (development)
    engine = create_engine(
        settings.database_url, 
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG
    )
else:
    # PostgreSQL configuration (production - Supabase)
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,    # Recycle connections every 5 minutes
        echo=settings.DEBUG  # Set to True for SQL query logging in debug
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
