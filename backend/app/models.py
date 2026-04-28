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


class SoilOutcome(Base):
    """Observed field outcome linked to a soil sample."""

    __tablename__ = "soil_outcomes"

    id = Column(Integer, primary_key=True, index=True)
    sample_id = Column(Integer, nullable=False, index=True)
    crop_planted = Column(String, nullable=False)
    fertilizer_used = Column(String, nullable=True)
    irrigation_pattern = Column(String, nullable=True)
    yield_value = Column(Float, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class LabSubmission(Base):
    """Metadata for lab-origin soil samples."""

    __tablename__ = "lab_submissions"

    id = Column(Integer, primary_key=True, index=True)
    sample_id = Column(Integer, nullable=False, index=True)
    lab_name = Column(String, nullable=True)
    report_reference = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class SensorReading(Base):
    """Optional readings from low-cost kits/sensors."""

    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, nullable=False, index=True)
    location = Column(String, nullable=True)
    ph = Column(Float, nullable=True)
    moisture = Column(Float, nullable=True)
    organic_matter = Column(Float, nullable=True)
    clay = Column(Float, nullable=True)
    phosphate = Column(Float, nullable=True)
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
