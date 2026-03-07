from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

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
