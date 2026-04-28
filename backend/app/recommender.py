from typing import Dict, List, Tuple

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


def _distance_to_range(value: float, min_value: float, max_value: float) -> float:
    """Distance from value to a target interval (0 if inside)."""

    if value < min_value:
        return min_value - value
    if value > max_value:
        return value - max_value
    return 0.0


def _range_fit_score(value: float, min_value: float, max_value: float, tolerance: float) -> float:
    """
    Convert distance from a target range into a 0-100 fitness score.

    - 100 when inside range
    - decreases linearly outside range
    """

    distance = _distance_to_range(value, min_value, max_value)
    if tolerance <= 0:
        return 100.0 if distance == 0 else 0.0
    return _clamp(100.0 - ((distance / tolerance) * 100.0), 0.0, 100.0)


def _crop_compatibility(
    ph: float,
    moisture: float,
    organic_matter: float,
    clay: float,
    phosphate: float,
) -> Tuple[List[str], List[Tuple[str, int]]]:
    """
    Return top crops and detailed compatibility scores.

    This is profile-based (continuous) rather than hard soil-type mapping.
    """

    crop_profiles = {
        "maize": {
            "ph": (5.5, 7.5, 1.5, 0.25),
            "moisture": (35.0, 60.0, 25.0, 0.20),
            "organic_matter": (2.0, 6.0, 4.0, 0.20),
            "clay": (15.0, 35.0, 20.0, 0.15),
            "phosphate": (10.0, 25.0, 12.0, 0.20),
        },
        "beans": {
            "ph": (6.0, 7.2, 1.2, 0.25),
            "moisture": (35.0, 65.0, 20.0, 0.20),
            "organic_matter": (2.5, 7.0, 4.0, 0.20),
            "clay": (10.0, 30.0, 20.0, 0.15),
            "phosphate": (12.0, 28.0, 12.0, 0.20),
        },
        "cassava": {
            "ph": (5.0, 7.0, 1.8, 0.25),
            "moisture": (25.0, 55.0, 25.0, 0.20),
            "organic_matter": (1.5, 5.0, 4.0, 0.20),
            "clay": (8.0, 28.0, 22.0, 0.15),
            "phosphate": (8.0, 22.0, 12.0, 0.20),
        },
        "groundnuts": {
            "ph": (5.5, 7.0, 1.5, 0.25),
            "moisture": (25.0, 50.0, 25.0, 0.20),
            "organic_matter": (1.5, 5.5, 4.0, 0.20),
            "clay": (5.0, 20.0, 20.0, 0.15),
            "phosphate": (10.0, 24.0, 12.0, 0.20),
        },
        "rice": {
            "ph": (5.0, 7.0, 1.8, 0.25),
            "moisture": (55.0, 85.0, 20.0, 0.20),
            "organic_matter": (2.0, 8.0, 4.0, 0.20),
            "clay": (25.0, 55.0, 18.0, 0.15),
            "phosphate": (8.0, 22.0, 12.0, 0.20),
        },
        "sugarcane": {
            "ph": (6.0, 8.0, 1.5, 0.25),
            "moisture": (45.0, 75.0, 20.0, 0.20),
            "organic_matter": (2.5, 8.5, 4.0, 0.20),
            "clay": (20.0, 45.0, 18.0, 0.15),
            "phosphate": (10.0, 28.0, 12.0, 0.20),
        },
        "cotton": {
            "ph": (5.8, 8.0, 1.5, 0.25),
            "moisture": (30.0, 60.0, 22.0, 0.20),
            "organic_matter": (2.0, 6.5, 4.0, 0.20),
            "clay": (15.0, 40.0, 20.0, 0.15),
            "phosphate": (10.0, 24.0, 12.0, 0.20),
        },
        "vegetables": {
            "ph": (6.0, 7.2, 1.2, 0.25),
            "moisture": (40.0, 70.0, 18.0, 0.20),
            "organic_matter": (3.0, 9.0, 3.5, 0.20),
            "clay": (10.0, 35.0, 20.0, 0.15),
            "phosphate": (12.0, 30.0, 10.0, 0.20),
        },
        "watermelon": {
            "ph": (5.5, 7.2, 1.4, 0.25),
            "moisture": (25.0, 50.0, 22.0, 0.20),
            "organic_matter": (2.0, 6.0, 4.0, 0.20),
            "clay": (5.0, 22.0, 18.0, 0.15),
            "phosphate": (10.0, 26.0, 12.0, 0.20),
        },
    }

    values = {
        "ph": ph,
        "moisture": moisture,
        "organic_matter": organic_matter,
        "clay": clay,
        "phosphate": phosphate,
    }

    scored: List[Tuple[str, int]] = []
    for crop, profile in crop_profiles.items():
        total = 0.0
        for metric, (min_v, max_v, tolerance, weight) in profile.items():
            fit = _range_fit_score(values[metric], min_v, max_v, tolerance)
            total += fit * weight
        scored.append((crop, int(round(_clamp(total, 0.0, 100.0)))))

    scored.sort(key=lambda item: item[1], reverse=True)
    top_crops = [name for name, _ in scored[:3]]
    return top_crops, scored[:5]


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
    # Recommended crops by profile fit
    # ------------------------------
    recommended_crops, crop_fit_scores = _crop_compatibility(
        ph=ph,
        moisture=moisture,
        organic_matter=organic_matter,
        clay=clay,
        phosphate=phosphate,
    )
    notes.append(
        "Recommended crops are selected by profile similarity (pH, moisture, OM, clay, phosphate)."
    )

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

    # ------------------------------
    # Confidence and guidance
    # ------------------------------
    top_score = crop_fit_scores[0][1] if crop_fit_scores else 0
    second_score = crop_fit_scores[1][1] if len(crop_fit_scores) > 1 else 0
    confidence_score = int(_clamp(top_score - (0.3 * (top_score - second_score)), 0, 100))

    if confidence_score < 55:
        confidence_label = "low"
    elif confidence_score < 75:
        confidence_label = "medium"
    else:
        confidence_label = "high"

    next_tests: List[str] = []
    if confidence_score < 75:
        next_tests.append("Measure nitrogen (N) and potassium (K) for better crop ranking.")
    if abs(ph - 6.5) > 1.5:
        next_tests.append("Recheck pH with a calibrated kit to confirm correction needs.")
    if phosphate < 8:
        next_tests.append("Run a full nutrient panel before final fertilizer dosage.")
    if moisture < 25 or moisture > 70:
        next_tests.append("Repeat moisture reading in 24h to reduce one-off sensor bias.")

    return {
        "fertility_score": int(_clamp(fertility_score, 0, 100)),
        "soil_type": soil_type,
        "notes": notes,
        "recommended_crops": recommended_crops,
        "crop_fit_scores": [{"crop": crop, "score": score} for crop, score in crop_fit_scores],
        "confidence_score": confidence_score,
        "confidence_label": confidence_label,
        "next_tests": next_tests,
        "fertilizer_suggestion": fertilizer_suggestion,
        "irrigation_suggestion": irrigation_suggestion,
    }
