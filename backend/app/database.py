import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Search for .env in current dir and backend root
backend_env = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=backend_env)
load_dotenv()

logger = logging.getLogger("adpilot.database")

DATABASE_URL = os.getenv("DATABASE_URL")

# Prioritize SQLite if explicitly configured, otherwise attempt PostgreSQL with fast fallback
if not DATABASE_URL or "sqlite" in DATABASE_URL:
    db_url = DATABASE_URL or "sqlite:///./adpilot.db"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
else:
    try:
        test_engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 1})
        with test_engine.connect() as conn:
            pass
        engine = test_engine
    except Exception as e:
        logger.warning(f"PostgreSQL unavailable ({e}). Using local SQLite: sqlite:///./adpilot.db")
        engine = create_engine("sqlite:///./adpilot.db", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
