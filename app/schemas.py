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
    fertilizer_suggestion: str
    irrigation_suggestion: str


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
