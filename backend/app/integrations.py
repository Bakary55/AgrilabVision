"""
Weather and location-aware farming advice (Gemini).

- If OPENWEATHER_API_KEY is set: uses OpenWeatherMap.
- Otherwise: uses Open-Meteo (free, no API key) — same coordinates.

GEMINI_API_KEY is required for /insights/farming and for /ai/soil-analyze.
"""

import os
from typing import Optional, Tuple

import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.schemas import FarmingInsightOut, WeatherCurrentOut

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    load_dotenv = None

try:
    import google.generativeai as genai
except Exception as exc:  # pragma: no cover
    genai = None
    _GENAI_IMPORT_ERROR = exc


router = APIRouter(tags=["integrations"])

OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def _ensure_dotenv() -> None:
    if load_dotenv:
        load_dotenv()


def _openweather_key() -> str:
    _ensure_dotenv()
    return (os.getenv("OPENWEATHER_API_KEY") or "").strip()


def _gemini_key() -> str:
    _ensure_dotenv()
    return (os.getenv("GEMINI_API_KEY") or "").strip()


def _normalize_model_name(model_name: str) -> str:
    if model_name.startswith("models/"):
        return model_name.split("/", 1)[1]
    return model_name


def _discover_candidate_models() -> list[str]:
    preferred = [
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
    ]
    discovered: list[str] = []
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
        discovered = []

    ordered: list[str] = []
    for name in preferred + discovered:
        if name not in ordered:
            ordered.append(name)
    return ordered


def _wmo_weather_description(code: int) -> str:
    """WMO weather code → short English label (Open-Meteo)."""

    table = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }
    return table.get(code, "Variable conditions")


async def _openweather_json(lat: float, lon: float) -> dict:
    key = _openweather_key()
    if not key:
        raise HTTPException(
            status_code=503,
            detail="OPENWEATHER_API_KEY not configured.",
        )
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(
            OPENWEATHER_URL,
            params={
                "lat": lat,
                "lon": lon,
                "appid": key,
                "units": "metric",
                "lang": "en",
            },
        )
    if resp.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Weather provider returned an error.",
        )
    return resp.json()


async def _open_meteo_json(lat: float, lon: float) -> dict:
    """Open-Meteo: no API key, for non-commercial / fair use."""

    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(
            OPEN_METEO_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
                "wind_speed_unit": "ms",
            },
        )
    if resp.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Open-Meteo weather service error.",
        )
    return resp.json()


def _weather_from_openweather(data: dict) -> WeatherCurrentOut:
    w = (data.get("weather") or [{}])[0]
    main = data.get("main") or {}
    wind = data.get("wind") or {}
    return WeatherCurrentOut(
        description=w.get("description", ""),
        temp_c=float(main.get("temp", 0)),
        humidity=int(main.get("humidity", 0) or 0),
        wind_speed_ms=float(wind.get("speed", 0) or 0),
        location_name=data.get("name"),
    )


def _weather_from_open_meteo(data: dict) -> WeatherCurrentOut:
    cur = data.get("current") or {}
    code = int(cur.get("weather_code", 0))
    return WeatherCurrentOut(
        description=_wmo_weather_description(code),
        temp_c=float(cur.get("temperature_2m", 0)),
        humidity=int(cur.get("relative_humidity_2m", 0) or 0),
        wind_speed_ms=float(cur.get("wind_speed_10m", 0) or 0),
        location_name=None,
    )


def _weather_narrative_from_out(out: WeatherCurrentOut) -> str:
    loc = out.location_name or "GPS position"
    return (
        f"{loc}: {out.description}, {out.temp_c:.1f}°C, "
        f"humidity {out.humidity}%, wind ~{out.wind_speed_ms:.1f} m/s"
    )


async def _fetch_weather_snapshot(lat: float, lon: float) -> Tuple[WeatherCurrentOut, str]:
    """OpenWeather if key is set, otherwise Open-Meteo (no account)."""

    if _openweather_key():
        data = await _openweather_json(lat, lon)
        out = _weather_from_openweather(data)
    else:
        data = await _open_meteo_json(lat, lon)
        out = _weather_from_open_meteo(data)
    return out, _weather_narrative_from_out(out)


class FarmingInsightBody(BaseModel):
    """Request body for Gemini + weather advisory."""

    lat: float = Field(..., description="Latitude WGS84")
    lon: float = Field(..., description="Longitude WGS84")
    language: str = Field("en", description="'en' or 'fr'")
    soil_summary: Optional[str] = Field(
        None,
        description="Optional short summary from a prior soil photo analysis.",
    )


@router.get("/weather/current", response_model=WeatherCurrentOut)
async def current_weather(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
) -> WeatherCurrentOut:
    """Current weather at coordinates (OpenWeatherMap if key set, else Open-Meteo)."""

    out, _ = await _fetch_weather_snapshot(lat, lon)
    return out


@router.post("/insights/farming", response_model=FarmingInsightOut)
async def farming_insights(body: FarmingInsightBody) -> FarmingInsightOut:
    """
    Combine live weather at (lat, lon) with Gemini to produce short farming advice
    (irrigation, risks, timing) in the requested language.
    """

    if genai is None:
        raise HTTPException(
            status_code=500,
            detail=f"Gemini SDK not installed: {_GENAI_IMPORT_ERROR}",
        )

    api_key = _gemini_key()
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY not configured.",
        )

    if body.language not in {"en", "fr"}:
        raise HTTPException(status_code=400, detail="language must be 'en' or 'fr'.")

    _, weather_summary = await _fetch_weather_snapshot(body.lat, body.lon)
    lang_label = "French" if body.language == "fr" else "English"

    soil_part = ""
    if body.soil_summary:
        soil_part = f"\nKnown soil context from photo analysis: {body.soil_summary}\n"

    prompt = (
        f"You are an agronomy advisor. Language: {lang_label}.\n"
        f"GPS coordinates: latitude {body.lat}, longitude {body.lon}.\n"
        f"Current weather: {weather_summary}.{soil_part}\n"
        "Give concise practical advice for a smallholder farmer: irrigation, "
        "fertilizer timing risk (rain), heat/cold stress, and whether conditions "
        "are favorable for field work today. "
        "Respond as plain text, 3–6 short paragraphs or bullet lines, no JSON."
    )

    genai.configure(api_key=api_key)
    advisory = ""
    for model_name in _discover_candidate_models():
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            advisory = (response.text or "").strip()
            if advisory:
                break
        except Exception:
            advisory = ""

    if not advisory:
        advisory = (
            "AI advisory is temporarily unavailable. Use current weather to decide irrigation: "
            "water less before heavy rain, monitor drainage, and avoid fertilizer spreading "
            "just before storms."
        )

    return FarmingInsightOut(
        advisory_text=advisory,
        weather_summary=weather_summary,
    )
