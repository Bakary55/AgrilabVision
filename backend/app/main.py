import csv
import io
from typing import List

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import models
from app.ai import router as ai_router
from app.auth import router as auth_router
from app.integrations import router as integrations_router
from app.database import Base, engine, get_db
from app.recommender import recommend_soil
from app.schemas import (
    LabSoilSampleCreate,
    LabSoilSampleOut,
    RecommendationOut,
    SensorReadingCreate,
    SensorReadingOut,
    SoilImportReport,
    SoilOutcomeCreate,
    SoilOutcomeOut,
    SoilSampleCreate,
    SoilSampleOut,
)

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
app.include_router(integrations_router)


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

    _validate_soil_payload(payload)
    sample = models.SoilSample(**payload.dict())
    db.add(sample)
    db.commit()
    db.refresh(sample)
    return sample


@app.post("/soil-samples/lab", response_model=LabSoilSampleOut)
def create_lab_soil_sample(
    payload: LabSoilSampleCreate, db: Session = Depends(get_db)
) -> LabSoilSampleOut:
    """Create a soil sample tagged as lab-assisted input."""

    sample_payload = SoilSampleCreate(
        farmer_name=payload.farmer_name,
        location=payload.location,
        ph=payload.ph,
        moisture=payload.moisture,
        organic_matter=payload.organic_matter,
        clay=payload.clay,
        phosphate=payload.phosphate,
    )
    _validate_soil_payload(sample_payload)
    sample = models.SoilSample(**sample_payload.dict())
    db.add(sample)
    db.flush()

    lab_meta = models.LabSubmission(
        sample_id=sample.id,
        lab_name=payload.lab_name,
        report_reference=payload.report_reference,
    )
    db.add(lab_meta)
    db.commit()
    db.refresh(sample)

    return LabSoilSampleOut(
        sample=sample,
        lab_name=payload.lab_name,
        report_reference=payload.report_reference,
    )


def _validate_soil_payload(payload: SoilSampleCreate) -> None:
    """Apply practical ranges to reduce invalid manual/CSV data."""

    if not (0 <= payload.moisture <= 100):
        raise HTTPException(status_code=400, detail="moisture must be between 0 and 100.")
    if not (0 <= payload.organic_matter <= 100):
        raise HTTPException(
            status_code=400, detail="organic_matter must be between 0 and 100."
        )
    if not (0 <= payload.clay <= 100):
        raise HTTPException(status_code=400, detail="clay must be between 0 and 100.")
    if not (0 <= payload.ph <= 14):
        raise HTTPException(status_code=400, detail="ph must be between 0 and 14.")
    if payload.phosphate < 0:
        raise HTTPException(status_code=400, detail="phosphate must be >= 0.")


@app.post("/soil-samples/import-csv", response_model=SoilImportReport)
async def import_soil_samples_csv(
    file: UploadFile = File(...), db: Session = Depends(get_db)
) -> SoilImportReport:
    """Import soil samples from a CSV file for bulk data entry."""

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file.")

    content = await file.read()
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8 encoded.")

    reader = csv.DictReader(io.StringIO(text))
    required_headers = {"ph", "moisture", "organic_matter", "clay", "phosphate"}
    if not reader.fieldnames or not required_headers.issubset(set(reader.fieldnames)):
        missing = sorted(required_headers.difference(set(reader.fieldnames or [])))
        raise HTTPException(
            status_code=400,
            detail=f"Missing required CSV columns: {', '.join(missing)}",
        )

    inserted_ids: List[int] = []
    errors: List[str] = []
    inserted_count = 0
    failed_count = 0

    for row_index, row in enumerate(reader, start=2):
        try:
            payload = SoilSampleCreate(
                farmer_name=(row.get("farmer_name") or None),
                location=(row.get("location") or None),
                ph=float(row.get("ph", "")),
                moisture=float(row.get("moisture", "")),
                organic_matter=float(row.get("organic_matter", "")),
                clay=float(row.get("clay", "")),
                phosphate=float(row.get("phosphate", "")),
            )
            _validate_soil_payload(payload)
            sample = models.SoilSample(**payload.dict())
            db.add(sample)
            db.flush()
            inserted_ids.append(sample.id)
            inserted_count += 1
        except Exception as exc:
            failed_count += 1
            errors.append(f"line {row_index}: {exc}")

    db.commit()
    return SoilImportReport(
        inserted_count=inserted_count,
        failed_count=failed_count,
        inserted_ids=inserted_ids,
        errors=errors,
    )


@app.post("/soil-samples/lab/import-csv", response_model=SoilImportReport)
async def import_lab_soil_samples_csv(
    file: UploadFile = File(...), db: Session = Depends(get_db)
) -> SoilImportReport:
    """Import lab-assisted soil samples from CSV."""

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file.")

    content = await file.read()
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8 encoded.")

    reader = csv.DictReader(io.StringIO(text))
    required_headers = {"ph", "moisture", "organic_matter", "clay", "phosphate"}
    if not reader.fieldnames or not required_headers.issubset(set(reader.fieldnames)):
        missing = sorted(required_headers.difference(set(reader.fieldnames or [])))
        raise HTTPException(
            status_code=400,
            detail=f"Missing required CSV columns: {', '.join(missing)}",
        )

    inserted_ids: List[int] = []
    errors: List[str] = []
    inserted_count = 0
    failed_count = 0

    for row_index, row in enumerate(reader, start=2):
        try:
            payload = SoilSampleCreate(
                farmer_name=(row.get("farmer_name") or None),
                location=(row.get("location") or None),
                ph=float(row.get("ph", "")),
                moisture=float(row.get("moisture", "")),
                organic_matter=float(row.get("organic_matter", "")),
                clay=float(row.get("clay", "")),
                phosphate=float(row.get("phosphate", "")),
            )
            _validate_soil_payload(payload)
            sample = models.SoilSample(**payload.dict())
            db.add(sample)
            db.flush()

            lab_meta = models.LabSubmission(
                sample_id=sample.id,
                lab_name=(row.get("lab_name") or None),
                report_reference=(row.get("report_reference") or None),
            )
            db.add(lab_meta)

            inserted_ids.append(sample.id)
            inserted_count += 1
        except Exception as exc:
            failed_count += 1
            errors.append(f"line {row_index}: {exc}")

    db.commit()
    return SoilImportReport(
        inserted_count=inserted_count,
        failed_count=failed_count,
        inserted_ids=inserted_ids,
        errors=errors,
    )


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


@app.post("/soil-samples/{sample_id}/outcomes", response_model=SoilOutcomeOut)
def create_soil_outcome(
    sample_id: int, payload: SoilOutcomeCreate, db: Session = Depends(get_db)
) -> models.SoilOutcome:
    """Store observed field outcomes for learning and future automation."""

    sample = db.query(models.SoilSample).filter(models.SoilSample.id == sample_id).first()
    if not sample:
        raise HTTPException(status_code=404, detail="Soil sample not found")

    outcome = models.SoilOutcome(sample_id=sample_id, **payload.dict())
    db.add(outcome)
    db.commit()
    db.refresh(outcome)
    return outcome


@app.get("/soil-samples/{sample_id}/outcomes", response_model=List[SoilOutcomeOut])
def list_soil_outcomes(
    sample_id: int, db: Session = Depends(get_db)
) -> List[models.SoilOutcome]:
    """List recorded outcomes for a given soil sample."""

    sample = db.query(models.SoilSample).filter(models.SoilSample.id == sample_id).first()
    if not sample:
        raise HTTPException(status_code=404, detail="Soil sample not found")

    return (
        db.query(models.SoilOutcome)
        .filter(models.SoilOutcome.sample_id == sample_id)
        .order_by(models.SoilOutcome.created_at.desc())
        .all()
    )


@app.post("/sensors/readings", response_model=SensorReadingOut)
def create_sensor_reading(
    payload: SensorReadingCreate, db: Session = Depends(get_db)
) -> models.SensorReading:
    """Store low-cost sensor readings for future automation."""

    reading = models.SensorReading(**payload.dict())
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading


@app.get("/sensors/readings", response_model=List[SensorReadingOut])
def list_sensor_readings(
    limit: int = 20, db: Session = Depends(get_db)
) -> List[models.SensorReading]:
    """List latest sensor readings."""

    safe_limit = max(1, min(limit, 200))
    return (
        db.query(models.SensorReading)
        .order_by(models.SensorReading.created_at.desc())
        .limit(safe_limit)
        .all()
    )


@app.get("/sensors/readings/{reading_id}/recommendation", response_model=RecommendationOut)
def get_sensor_reading_recommendation(
    reading_id: int, db: Session = Depends(get_db)
) -> RecommendationOut:
    """Generate recommendation from a sensor reading when all key fields are present."""

    reading = (
        db.query(models.SensorReading).filter(models.SensorReading.id == reading_id).first()
    )
    if not reading:
        raise HTTPException(status_code=404, detail="Sensor reading not found")

    missing = []
    for field_name in ["ph", "moisture", "organic_matter", "clay", "phosphate"]:
        if getattr(reading, field_name) is None:
            missing.append(field_name)

    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Sensor reading missing required fields for recommendation: {', '.join(missing)}",
        )

    return recommend_soil(
        ph=float(reading.ph),
        moisture=float(reading.moisture),
        organic_matter=float(reading.organic_matter),
        clay=float(reading.clay),
        phosphate=float(reading.phosphate),
    )
