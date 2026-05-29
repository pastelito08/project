from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Creates the connection to the database using the URL from .env
engine = create_engine(settings.DATABASE_URL)

# Each request gets its own session, closed when done
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class all models will inherit from
Base = declarative_base()

# Dependency — used in route functions to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()