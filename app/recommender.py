from typing import Dict, List

# ------------------------------
# Rule-based soil recommender
# ------------------------------


def _clamp(value: float, minimum: float, maximum: float) -> float:
    """Keep a number inside a given range."""

    return max(minimum, min(maximum, value))


def _score_from_range(value: float, min_value: float, max_value: float) -> float:
    """Convert a value to a 0–100 score based on a min/max range."""

    if max_value == min_value:
        return 0.0
    return ((value - min_value) / (max_value - min_value)) * 100.0


def recommend_soil(
    ph: float,
    moisture: float,
    organic_matter: float,
    clay: float,
    phosphate: float,
) -> Dict[str, object]:
    """
    Return a simple recommendation package based on soil inputs.

    This logic is deterministic and intentionally simple for clarity.
    """

    notes: List[str] = []

    # ------------------------------
    # Soil type classification
    # ------------------------------
    if clay >= 40:
        soil_type = "clay"
    elif clay <= 20:
        soil_type = "sandy"
    elif 20 < clay < 40:
        soil_type = "loam"
    else:
        soil_type = "unknown"

    notes.append(f"Soil type classified as '{soil_type}' based on clay content.")

    # ------------------------------
    # Fertility score (0–100)
    # ------------------------------
    # Phosphorus (phosphate) and organic matter are strong indicators.
    phosphate_score = _clamp(_score_from_range(phosphate, 0, 30), 0, 100)
    organic_score = _clamp(_score_from_range(organic_matter, 0, 10), 0, 100)

    # pH score: best near 6.5, weaker as it moves away.
    ph_distance = abs(ph - 6.5)
    ph_score = _clamp(100 - (ph_distance * 20), 0, 100)

    # Moisture: target range 30–60.
    if 30 <= moisture <= 60:
        moisture_score = 100.0
    elif moisture < 30:
        moisture_score = _clamp(_score_from_range(moisture, 0, 30), 0, 100)
    else:
        moisture_score = _clamp(100 - _score_from_range(moisture, 60, 100), 0, 100)

    # Weighted average for a realistic but simple fertility score.
    fertility_score = round(
        (0.35 * organic_score)
        + (0.25 * phosphate_score)
        + (0.25 * ph_score)
        + (0.15 * moisture_score)
    )

    notes.append("Fertility score combines organic matter, phosphate, pH, and moisture.")

    # ------------------------------
    # Recommended crops by soil type
    # ------------------------------
    if soil_type == "sandy":
        recommended_crops = ["groundnuts", "watermelon", "cassava"]
    elif soil_type == "loam":
        recommended_crops = ["maize", "beans", "vegetables"]
    elif soil_type == "clay":
        recommended_crops = ["rice", "sugarcane", "cotton"]
    else:
        recommended_crops = ["maize", "beans"]

    # ------------------------------
    # Fertilizer suggestion
    # ------------------------------
    if ph < 5.5:
        fertilizer_suggestion = "Apply agricultural lime to raise pH."
        notes.append("Soil is acidic; lime can improve nutrient availability.")
    elif ph > 7.5:
        fertilizer_suggestion = "Apply sulfur or organic matter to lower pH."
        notes.append("Soil is alkaline; sulfur/organic matter can help balance pH.")
    elif phosphate < 10:
        fertilizer_suggestion = "Add phosphate-rich fertilizer (e.g., SSP/DAP)."
        notes.append("Phosphate is low; use a phosphate fertilizer.")
    else:
        fertilizer_suggestion = "Use a balanced NPK fertilizer as needed."
        notes.append("Nutrients look reasonable; maintain with balanced NPK.")

    # ------------------------------
    # Irrigation suggestion
    # ------------------------------
    if moisture < 30:
        irrigation_suggestion = "Increase irrigation; soil moisture is low."
        notes.append("Moisture is low; more frequent watering is advised.")
    elif moisture > 60:
        irrigation_suggestion = "Reduce irrigation; soil is already moist."
        notes.append("Moisture is high; reduce watering to avoid waterlogging.")
    else:
        irrigation_suggestion = "Maintain current irrigation schedule."
        notes.append("Moisture is in a healthy range.")

    return {
        "fertility_score": int(_clamp(fertility_score, 0, 100)),
        "soil_type": soil_type,
        "notes": notes,
        "recommended_crops": recommended_crops,
        "fertilizer_suggestion": fertilizer_suggestion,
        "irrigation_suggestion": irrigation_suggestion,
    }
