import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

logger = logging.getLogger("uvicorn.error")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/subscription_pause_db")
FALLBACK_DATABASE_URL = os.getenv("FALLBACK_DATABASE_URL", "sqlite:///./subscription_pause.db")

engine = None
SessionLocal = None

try:
    # Attempt connecting to configured PostgreSQL database
    temp_engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    with temp_engine.connect():
        pass
    engine = temp_engine
    logger.info("Connected successfully to PostgreSQL database.")
except Exception as e:
    logger.warning(
        f"PostgreSQL connection to {DATABASE_URL} failed ({e}). "
        f"Falling back to local SQLite ({FALLBACK_DATABASE_URL}) for active development and tests."
    )
    engine = create_engine(
        FALLBACK_DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in FALLBACK_DATABASE_URL else {}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
