import json
import os
from typing import List

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.schemas import AISoilRecommendationOut

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - optional dependency
    load_dotenv = None

try:
    import google.generativeai as genai
except Exception as exc:  # pragma: no cover - handled at runtime
    genai = None
    _GENAI_IMPORT_ERROR = exc


router = APIRouter(prefix="/ai", tags=["ai"])


class _AIResponse(BaseModel):
    soil_type: str
    moisture_estimate: str
    recommended_crops: List[str]
    fertilizer_recommendations: List[str]
    notes: List[str]


def _get_api_key() -> str:
    """Load Gemini API key from .env or environment."""

    if load_dotenv:
        load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GEMINI_API_KEY not configured.",
        )
    return api_key


def _build_prompt(language: str) -> str:
    """Create a strict JSON-only prompt in the requested language."""

    language_label = "French" if language == "fr" else "English"
    return (
        "You are an agronomy assistant. Analyze the soil photo and respond ONLY in JSON.\n"
        "Language: " + language_label + ".\n"
        "Return this JSON schema:\n"
        "{\n"
        '  "soil_type": "sandy|loam|clay|unknown",\n'
        '  "moisture_estimate": "low|medium|high (with short explanation)",\n'
        '  "recommended_crops": ["crop1", "crop2", "crop3"],\n'
        '  "fertilizer_recommendations": ["crop: fertilizer suggestion", "..."],\n'
        '  "notes": ["short note 1", "short note 2"]\n'
        "}\n"
        "Be realistic and avoid hallucinations. If unsure, use 'unknown'."
    )


@router.post("/soil-analyze", response_model=AISoilRecommendationOut)
async def analyze_soil_photo(
    image: UploadFile = File(...),
    language: str = Form("en"),
) -> AISoilRecommendationOut:
    """Analyze a soil photo with Gemini and return recommendations."""

    if genai is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gemini SDK not installed: {_GENAI_IMPORT_ERROR}",
        )

    if language not in {"en", "fr"}:
        raise HTTPException(status_code=400, detail="Language must be 'en' or 'fr'.")

    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload a valid image file.")

    api_key = _get_api_key()
    genai.configure(api_key=api_key)

    image_bytes = await image.read()
    prompt = _build_prompt(language)

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(
        [
            {"mime_type": image.content_type, "data": image_bytes},
            prompt,
        ]
    )

    # Try to parse JSON strictly. If parsing fails, return a helpful error.
    try:
        text = response.text.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:].strip()
        data = json.loads(text)
        parsed = _AIResponse(**data)
        return AISoilRecommendationOut(**parsed.dict())
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="AI response could not be parsed. Try another image.",
        )
