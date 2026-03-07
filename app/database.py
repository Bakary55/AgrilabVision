from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# ------------------------------
# Database setup (SQLite)
# ------------------------------

# This creates a local SQLite file called "agrilabvision.db".
DATABASE_URL = "sqlite:///./agrilabvision.db"

# "check_same_thread" allows SQLite to be used with FastAPI's async handling.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

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
