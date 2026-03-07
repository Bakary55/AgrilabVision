from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import models
from app.ai import router as ai_router
from app.auth import router as auth_router
from app.database import Base, engine, get_db
from app.recommender import recommend_soil
from app.schemas import RecommendationOut, SoilSampleCreate, SoilSampleOut

# ------------------------------
# FastAPI app
# ------------------------------

app = FastAPI()

# Allow frontend (or file://) to call the API during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """Create tables when the app starts."""

    Base.metadata.create_all(bind=engine)


# Include authentication routes under /auth.
app.include_router(auth_router)
app.include_router(ai_router)


# ------------------------------
# API endpoints
# ------------------------------


@app.get("/")
def read_root() -> dict:
    """Health check endpoint."""

    return {"status": "ok"}


@app.post("/soil-samples", response_model=SoilSampleOut)
def create_soil_sample(
    payload: SoilSampleCreate, db: Session = Depends(get_db)
) -> models.SoilSample:
    """Create a new soil sample in SQLite."""

    sample = models.SoilSample(**payload.dict())
    db.add(sample)
    db.commit()
    db.refresh(sample)
    return sample


@app.get("/soil-samples", response_model=List[SoilSampleOut])
def list_soil_samples(db: Session = Depends(get_db)) -> List[models.SoilSample]:
    """List all samples, newest first."""

    return (
        db.query(models.SoilSample)
        .order_by(models.SoilSample.created_at.desc())
        .all()
    )


@app.get("/soil-samples/{sample_id}", response_model=SoilSampleOut)
def get_soil_sample(
    sample_id: int, db: Session = Depends(get_db)
) -> models.SoilSample:
    """Fetch a single sample by id or return 404."""

    sample = db.query(models.SoilSample).filter(models.SoilSample.id == sample_id).first()
    if not sample:
        raise HTTPException(status_code=404, detail="Soil sample not found")
    return sample


@app.get("/soil-samples/{sample_id}/recommendation", response_model=RecommendationOut)
def get_recommendation(
    sample_id: int, db: Session = Depends(get_db)
) -> RecommendationOut:
    """Return a simple recommendation for a soil sample."""

    sample = db.query(models.SoilSample).filter(models.SoilSample.id == sample_id).first()
    if not sample:
        raise HTTPException(status_code=404, detail="Soil sample not found")

    return recommend_soil(
        ph=sample.ph,
        moisture=sample.moisture,
        organic_matter=sample.organic_matter,
        clay=sample.clay,
        phosphate=sample.phosphate,
    )
