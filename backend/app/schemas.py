from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, ConfigDict

# ------------------------------
# Pydantic schemas (API shapes)
# ------------------------------


class SoilSampleCreate(BaseModel):
    """Input validation when creating a soil sample."""

    farmer_name: Optional[str] = Field(None, example="Amina")
    location: Optional[str] = Field(None, example="Plot 7")
    ph: float = Field(..., example=6.5)
    moisture: float = Field(..., example=22.5)  # percentage (0-100)
    organic_matter: float = Field(..., example=3.1)  # percentage (0-100)
    clay: float = Field(..., example=18.0)  # percentage (0-100)
    phosphate: float = Field(..., example=12.4)


class SoilSampleOut(BaseModel):
    """Output schema for a soil sample (includes id and created_at)."""

    id: int
    farmer_name: Optional[str]
    location: Optional[str]
    ph: float
    moisture: float
    organic_matter: float
    clay: float
    phosphate: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecommendationOut(BaseModel):
    """Output schema for soil recommendations."""

    fertility_score: int
    soil_type: str
    notes: List[str]
    recommended_crops: List[str]
    crop_fit_scores: List[dict]
    confidence_score: int
    confidence_label: Literal["low", "medium", "high"]
    next_tests: List[str]
    fertilizer_suggestion: str
    irrigation_suggestion: str


class SoilImportReport(BaseModel):
    """Report returned after CSV import."""

    inserted_count: int
    failed_count: int
    inserted_ids: List[int]
    errors: List[str]


class SoilOutcomeCreate(BaseModel):
    """Input for storing observed outcomes after recommendations."""

    crop_planted: str = Field(..., example="maize")
    fertilizer_used: Optional[str] = Field(None, example="NPK 15-15-15")
    irrigation_pattern: Optional[str] = Field(None, example="every 2 days")
    yield_value: Optional[float] = Field(None, ge=0, example=4.2)
    notes: Optional[str] = Field(None, example="Good growth after week 3")


class SoilOutcomeOut(BaseModel):
    """Output schema for persisted field outcomes."""

    id: int
    sample_id: int
    crop_planted: str
    fertilizer_used: Optional[str]
    irrigation_pattern: Optional[str]
    yield_value: Optional[float]
    notes: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LabSoilSampleCreate(SoilSampleCreate):
    """Lab-assisted soil sample entry."""

    lab_name: Optional[str] = Field(None, example="AgriLab Central")
    report_reference: Optional[str] = Field(None, example="LAB-2026-04-27-001")


class LabSoilSampleOut(BaseModel):
    """Response for lab-assisted sample creation."""

    sample: SoilSampleOut
    lab_name: Optional[str]
    report_reference: Optional[str]


class SensorReadingCreate(BaseModel):
    """Input payload for optional low-cost sensor ingestion."""

    device_id: str = Field(..., example="sensor-kit-01")
    location: Optional[str] = Field(None, example="Plot 7")
    ph: Optional[float] = Field(None, ge=0, le=14)
    moisture: Optional[float] = Field(None, ge=0, le=100)
    organic_matter: Optional[float] = Field(None, ge=0, le=100)
    clay: Optional[float] = Field(None, ge=0, le=100)
    phosphate: Optional[float] = Field(None, ge=0)


class SensorReadingOut(BaseModel):
    """Persisted sensor reading."""

    id: int
    device_id: str
    location: Optional[str]
    ph: Optional[float]
    moisture: Optional[float]
    organic_matter: Optional[float]
    clay: Optional[float]
    phosphate: Optional[float]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserRegister(BaseModel):
    """Input data when registering a new user."""

    first_name: str = Field(..., example="Amina")
    last_name: str = Field(..., example="Njoroge")
    email: str = Field(..., example="amina@example.com")
    age: int = Field(..., ge=13, example=21)
    user_type: Literal["farmer", "student", "researcher"] = Field(
        ..., example="farmer"
    )
    password: str = Field(..., example="StrongP@ssw0rd")


class UserLogin(BaseModel):
    """Input data when logging in."""

    email: str = Field(..., example="amina@example.com")
    password: str = Field(..., example="StrongP@ssw0rd")


class UserOut(BaseModel):
    """Public user data returned by the API (no password)."""

    id: int
    first_name: str
    last_name: str
    email: str
    age: int
    user_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PasswordResetRequest(BaseModel):
    """Input for requesting a password reset."""

    email: str = Field(..., example="amina@example.com")


class PasswordResetConfirm(BaseModel):
    """Input for confirming a password reset with a new password."""

    reset_token: str = Field(..., example="reset-token-from-email")
    new_password: str = Field(..., example="NewStr0ngP@ss")


class AISoilRecommendationOut(BaseModel):
    """AI-based recommendation response for a soil photo."""

    soil_type: str
    moisture_estimate: str
    recommended_crops: List[str]
    fertilizer_recommendations: List[str]
    notes: List[str]
    photo_quality_score: int
    photo_quality_label: Literal["low", "medium", "high"]
    photo_quality_notes: List[str]


class WeatherCurrentOut(BaseModel):
    """OpenWeatherMap snapshot for the mobile app."""

    description: str
    temp_c: float
    humidity: int
    wind_speed_ms: float
    location_name: Optional[str] = None


class FarmingInsightOut(BaseModel):
    """Gemini advisory enriched with live weather."""

    advisory_text: str
    weather_summary: str
