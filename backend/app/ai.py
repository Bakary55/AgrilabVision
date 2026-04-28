import json
import os
import re
from typing import List, Optional

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
        backend_env = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
        load_dotenv(backend_env)
        load_dotenv()

    api_key = (os.getenv("GEMINI_API_KEY") or "").strip()
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


def _normalize_model_name(model_name: str) -> str:
    """Convert 'models/xyz' names to 'xyz' for GenerativeModel()."""

    if model_name.startswith("models/"):
        return model_name.split("/", 1)[1]
    return model_name


def _discover_candidate_models() -> List[str]:
    """
    Discover usable models for this API key.

    Prefer modern flash models, then fall back to any model that supports
    `generateContent`.
    """

    preferred = [
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
    ]
    discovered: List[str] = []
    try:
        for model in genai.list_models():
            name = _normalize_model_name(getattr(model, "name", ""))
            methods = getattr(model, "supported_generation_methods", []) or []
            if (
                name
                and "generateContent" in methods
                and "gemini" in name.lower()
                and name not in discovered
            ):
                discovered.append(name)
    except Exception:
        # If listing models fails, we still try preferred defaults below.
        discovered = []

    ordered: List[str] = []
    for name in preferred + discovered:
        if name not in ordered:
            ordered.append(name)
    return ordered


def _photo_quality_from_bytes(image_bytes: bytes) -> tuple[int, str, List[str]]:
    """
    Estimate photo quality from byte-size heuristics.

    This is intentionally simple and safe (no heavy CV dependency).
    """

    size_kb = len(image_bytes) / 1024.0
    notes: List[str] = []

    if size_kb < 80:
        score = 28
        label = "low"
        notes.append("Image appears too small or compressed; details may be lost.")
    elif size_kb < 180:
        score = 52
        label = "medium"
        notes.append("Image quality is acceptable but could be improved.")
    elif size_kb < 900:
        score = 82
        label = "high"
        notes.append("Image detail is good for visual soil analysis.")
    else:
        score = 72
        label = "high"
        notes.append("Large image received; quality should be sufficient.")

    notes.append("For best results: keep soil centered and avoid heavy shadows/plants.")
    return score, label, notes


def _fallback_ai_response(language: str, reason: Optional[str] = None) -> AISoilRecommendationOut:
    """Return a safe fallback payload when Gemini is unavailable."""

    quality_score = 35
    quality_label = "low"
    quality_notes = [
        "Photo quality could not be validated through AI service.",
        "Retake with clear light and mostly visible soil area.",
    ]

    if language == "fr":
        notes = [
            "Analyse de secours: service Gemini indisponible pour le moment.",
            "Le type de sol n'a pas pu etre determine depuis la photo seule.",
            "Ajoutez les mesures manuelles (pH, humidite, MO, argile, phosphate) pour obtenir des recommandations precises.",
        ]
    else:
        notes = [
            "Fallback analysis: Gemini service is currently unavailable.",
            "Soil type could not be determined from the photo only.",
            "Add manual soil metrics (pH, moisture, OM, clay, phosphate) to get precise recommendations.",
        ]
    # Keep technical details server-side only; do not expose to users.
    _ = reason

    return AISoilRecommendationOut(
        soil_type="unknown",
        moisture_estimate="medium (fallback estimate)",
        recommended_crops=[],
        fertilizer_recommendations=["Run manual soil measurements before choosing fertilizer dosage."],
        notes=notes,
        photo_quality_score=quality_score,
        photo_quality_label=quality_label,
        photo_quality_notes=quality_notes,
    )


def _parse_ai_json_response(text: str) -> _AIResponse:
    """
    Parse Gemini output into the strict response schema.

    Gemini can occasionally wrap JSON in markdown fences or extra prose.
    """

    candidate = text.strip()
    if candidate.startswith("```"):
        candidate = re.sub(r"^```(?:json)?\s*", "", candidate, flags=re.IGNORECASE)
        candidate = re.sub(r"\s*```$", "", candidate)

    try:
        data = json.loads(candidate)
        return _AIResponse(**data)
    except Exception:
        # Try to recover first JSON object/array from mixed content.
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        data = json.loads(candidate[start : end + 1])
        return _AIResponse(**data)


def _classify_gemini_error(exc: Optional[Exception]) -> tuple[int, str]:
    """Map Gemini backend errors to user-facing HTTP status/details."""

    if exc is None:
        return (
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "AI analysis is temporarily unavailable. Please retry in a moment.",
        )

    err = str(exc).lower()
    if "reported as leaked" in err:
        return (
            status.HTTP_403_FORBIDDEN,
            "Gemini API key is blocked (reported as leaked). Generate a new key and update backend/.env.",
        )
    if "api key not valid" in err or "permission_denied" in err or "403" in err:
        return (
            status.HTTP_403_FORBIDDEN,
            "Gemini API key is invalid or unauthorized. Check backend/.env and billing/quota settings.",
        )
    if (
        "quota" in err
        or "rate limit" in err
        or "resource_exhausted" in err
        or "prepayment credits are depleted" in err
        or "credits are depleted" in err
    ):
        return (
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Gemini quota/rate limit reached. Retry later or increase API quota.",
        )
    return (
        status.HTTP_503_SERVICE_UNAVAILABLE,
        "AI analysis is temporarily unavailable. Please retry in a moment.",
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
    quality_score, quality_label, quality_notes = _photo_quality_from_bytes(image_bytes)
    prompt = _build_prompt(language)

    candidate_models = _discover_candidate_models()
    response = None
    last_error: Optional[Exception] = None
    for model_name in candidate_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                [
                    {"mime_type": image.content_type, "data": image_bytes},
                    prompt,
                ]
            )
            break
        except Exception as exc:
            last_error = exc
            continue

    if response is None:
        status_code, detail = _classify_gemini_error(last_error)
        raise HTTPException(
            status_code=status_code,
            detail=detail,
        )

    # Parse JSON from model output with fence/prose recovery.
    try:
        parsed = _parse_ai_json_response(response.text)
        parsed.notes = parsed.notes + [
            "Photo-based estimation completed. Add manual values for higher precision."
        ]
        return AISoilRecommendationOut(
            **parsed.model_dump(),
            photo_quality_score=quality_score,
            photo_quality_label=quality_label,
            photo_quality_notes=quality_notes,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI returned an unexpected format. Please retry with another photo.",
        )
