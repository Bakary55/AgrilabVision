import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# ------------------------------
# Database setup (SQLite)
# ------------------------------

# Prefer DATABASE_URL from environment (Render/Postgres), fallback to local SQLite.
DATABASE_URL = (os.getenv("DATABASE_URL") or "sqlite:///./agrilabvision.db").strip()
if DATABASE_URL.startswith("postgres://"):
    # Render may provide postgres://; SQLAlchemy expects postgresql://
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if os.getenv("RENDER") and DATABASE_URL.startswith("sqlite"):
    raise RuntimeError(
        "DATABASE_URL points to SQLite in Render. Configure a managed Postgres DATABASE_URL."
    )

# "check_same_thread" is needed only for local SQLite.
is_sqlite = DATABASE_URL.startswith("sqlite")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if is_sqlite else {},
)

# SessionLocal will be used to create and manage DB sessions.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the class we will use for all SQLAlchemy models.
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session and closes it after use.

    Keeping this in one place makes it easy to reuse across endpoints.
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
