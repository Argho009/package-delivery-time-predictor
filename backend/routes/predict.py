"""
routes/predict.py — POST /api/predict
Orchestrates: OSRM Routing → Weather API (display only) → ML Prediction → DB log → Response
Note: Weather is shown in the UI but NOT used as an ML feature.
      Real datasets (Kaggle) don't have weather, so ML uses logistics-only features.
"""

import time
import uuid
import logging
from flask import Blueprint, request, jsonify

from database.db import db
from database.models import PredictionLog
from services.maps_service import get_route_info
from services.weather_service import get_weather
from models.predict import predict_all

logger = logging.getLogger(__name__)
predict_bp = Blueprint("predict", __name__, url_prefix="/api")


def _validate_payload(data: dict) -> list:
    """Return list of validation error strings (empty = valid)."""
    errors = []
    required = ["origin", "destination", "package_weight_kg", "package_type", "priority"]
    # shipping_mode is optional (defaults to ROAD)
    for field in required:
        if not data.get(field):
            errors.append(f"'{field}' is required.")

    if data.get("package_weight_kg") is not None:
        try:
            w = float(data["package_weight_kg"])
            if w <= 0:
                errors.append("'package_weight_kg' must be greater than 0.")
        except (ValueError, TypeError):
            errors.append("'package_weight_kg' must be a number.")

    valid_types = {"SMALL", "MEDIUM", "LARGE", "FRAGILE", "PERISHABLE"}
    if data.get("package_type") and data["package_type"].upper() not in valid_types:
        errors.append(f"'package_type' must be one of: {', '.join(valid_types)}")

    valid_priorities = {"STANDARD", "EXPRESS", "OVERNIGHT"}
    if data.get("priority") and data["priority"].upper() not in valid_priorities:
        errors.append(f"'priority' must be one of: {', '.join(valid_priorities)}")

    valid_modes = {"ROAD", "AIR", "RAIL", "SEA"}
    if data.get("shipping_mode") and data["shipping_mode"].upper() not in valid_modes:
        errors.append(f"'shipping_mode' must be one of: {', '.join(valid_modes)}")

    return errors


@predict_bp.route("/predict", methods=["POST"])
def predict():
    """
    POST /api/predict

    Request body (JSON):
        {
            "origin":             "Mumbai",
            "destination":        "Pune",
            "package_weight_kg":  5.0,
            "package_type":       "MEDIUM",
            "priority":           "STANDARD"
        }

    Response:
        {
            "request_id": "...",
            "origin": {...},
            "destination": {...},
            "route": { distance_km, traffic_duration_min, traffic_level },
            "weather": { weather_condition, temperature_celsius, ... },
            "predictions": {
                "xgboost": float,
                "random_forest": float,
                "linear_regression": float,
                "recommended_model": str,
                "recommended_hours": float,
                "confidence_low": float,
                "confidence_high": float
            },
            "response_time_ms": int
        }
    """
    t_start = time.time()
    data = request.get_json(force=True, silent=True) or {}

    # Validate
    errors = _validate_payload(data)
    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400

    origin        = data["origin"].strip()
    destination   = data["destination"].strip()
    weight        = float(data["package_weight_kg"])
    pkg_type      = data["package_type"].upper()
    priority      = data["priority"].upper()
    shipping_mode = data.get("shipping_mode", "ROAD").upper()
    request_id    = str(uuid.uuid4())

    # ── Step 1: OpenStreetMap / OSRM Routing ─────────────────
    try:
        route = get_route_info(origin, destination)
    except ValueError as e:
        logger.error("Maps API error: %s", e)
        return jsonify({"error": "Maps API error", "details": str(e)}), 502

    # ── Step 2: OpenWeather (for destination city) ─────────────
    # Extract city name from destination (first part before comma)
    dest_city = destination.split(",")[0].strip()
    try:
        weather = get_weather(dest_city)
    except ValueError as e:
        logger.error("Weather API error: %s", e)
        return jsonify({"error": "Weather API error", "details": str(e)}), 502

    # ── Step 3: ML Prediction (logistics features only — no weather) ──
    try:
        predictions = predict_all(
            distance_km          = route["distance_km"],
            traffic_duration_min = route["traffic_duration_min"],
            traffic_level        = route["traffic_level"],
            package_weight_kg    = weight,
            package_type         = pkg_type,
            priority             = priority,
            shipping_mode        = shipping_mode,
        )
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 503

    response_ms = int((time.time() - t_start) * 1000)

    # ── Step 4: Log to DB ──────────────────────────────────────
    try:
        log = PredictionLog(
            request_id           = request_id,
            origin               = route["origin_address"],
            destination          = route["destination_address"],
            distance_km          = route["distance_km"],
            traffic_duration_min = route["traffic_duration_min"],
            traffic_level        = route["traffic_level"],
            weather_condition    = weather["weather_condition"],   # display only
            temperature_celsius  = weather["temperature_celsius"],
            wind_speed_kmh       = weather["wind_speed_kmh"],
            precipitation_mm     = weather["precipitation_mm"],
            package_weight_kg    = weight,
            package_type         = pkg_type,
            priority             = priority,
            predicted_xgboost    = predictions.get("xgboost"),
            predicted_rf         = predictions.get("random_forest"),
            predicted_lr         = predictions.get("linear_regression"),
            recommended_model    = predictions["recommended_model"],
            recommended_hours    = predictions["recommended_hours"],
            api_response_ms      = response_ms,
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        logger.warning("Failed to log prediction to DB: %s", e)
        db.session.rollback()

    return jsonify({
        "request_id": request_id,
        "origin": {
            "input":   origin,
            "resolved": route["origin_address"],
        },
        "destination": {
            "input":   destination,
            "resolved": route["destination_address"],
        },
        "route": {
            "distance_km":          route["distance_km"],
            "base_duration_min":    route["base_duration_min"],
            "traffic_duration_min": route["traffic_duration_min"],
            "traffic_level":        route["traffic_level"],
        },
        "weather": {
            "condition":           weather["weather_condition"],
            "temperature_celsius": weather["temperature_celsius"],
            "wind_speed_kmh":      weather["wind_speed_kmh"],
            "precipitation_mm":    weather["precipitation_mm"],
            "description":         weather.get("description", ""),
        },
        "package": {
            "weight_kg":     weight,
            "type":          pkg_type,
            "priority":      priority,
            "shipping_mode": shipping_mode,
        },
        "predictions": predictions,
        "response_time_ms": response_ms,
    }), 200
