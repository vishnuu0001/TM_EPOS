from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine.url import make_url
from typing import Generator
from .config import settings
import os

# Ensure SQLite database directory exists (use DATABASE_URL path, not repo paths)
def _ensure_sqlite_dir(database_url: str) -> None:
    try:
        url = make_url(database_url)
    except Exception:
        return

    if url.drivername != "sqlite":
        return

    # sqlite memory does not need a directory
    if url.database in (None, "", ":memory:"):
        return

    db_path = url.database
    # Handle relative paths like sqlite:///./tmp/epos.db
    if not os.path.isabs(db_path):
        db_path = os.path.abspath(db_path)

    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

_ensure_sqlite_dir(settings.DATABASE_URL)

# Create database engine with SQLite-specific settings
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables
    """
    Base.metadata.create_all(bind=engine)
