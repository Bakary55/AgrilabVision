from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from app.database import Base

# ------------------------------
# SQLAlchemy models
# ------------------------------


class SoilSample(Base):
    """Represents a soil sample record in the database."""

    __tablename__ = "soil_samples"

    # Primary key ID (auto-incremented).
    id = Column(Integer, primary_key=True, index=True)

    # Optional metadata fields about the sample.
    farmer_name = Column(String, nullable=True)
    location = Column(String, nullable=True)

    # Core soil measurements.
    ph = Column(Float, nullable=False)
    moisture = Column(Float, nullable=False)  # percentage (0-100)
    organic_matter = Column(Float, nullable=False)  # percentage (0-100)
    clay = Column(Float, nullable=False)  # percentage (0-100)
    phosphate = Column(Float, nullable=False)

    # Timestamp for when the sample was created.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class User(Base):
    """Represents a user account for authentication."""

    __tablename__ = "users"

    # Primary key ID (auto-incremented).
    id = Column(Integer, primary_key=True, index=True)

    # Basic user identity fields.
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    # Email is unique and indexed for fast lookups.
    email = Column(String, unique=True, index=True, nullable=False)

    # Age is validated in the API (must be >= 13).
    age = Column(Integer, nullable=False)

    # Farmer, student, or researcher.
    user_type = Column(String, nullable=False)

    # Store ONLY the hashed password (never the raw password).
    password_hash = Column(String, nullable=False)

    # Password reset fields (nullable until used).
    reset_token = Column(String, nullable=True)
    reset_token_expiration = Column(DateTime, nullable=True)

    # When the user was created.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
