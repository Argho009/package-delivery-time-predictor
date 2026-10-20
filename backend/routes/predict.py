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
from services.weather_service import get_route_weather, get_weather_by_coords
from services.multimodal_service import check_multimodal_options
from models.predict import predict_all, predict_ensemble, explain_prediction
from utils.sustainability import calculate_carbon_footprint

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

    valid_types = {"SMALL", "MEDIUM", "LARGE", "HEAVY", "FRAGILE", "PERISHABLE", "OVERSIZED", "HAZARDOUS"}
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

    # ── Step 2: OpenWeather (Multi-point route weather) ───────
    try:
        weather = get_route_weather(route["waypoints"])
    except ValueError as e:
        logger.error("Weather API error: %s", e)
        return jsonify({"error": "Weather API error", "details": str(e)}), 502

    # ── Step 3: Overall ML Ensemble Prediction ──
    try:
        eff_dist = route["distance_km"]
        eff_traffic_min = route["traffic_duration_min"]
        eff_traffic_level = route["traffic_level"]
        if shipping_mode == "AIR":
            eff_dist = route["distance_km"] * 0.85
            eff_traffic_min = (eff_dist / 600.0) * 60.0 + 180.0
            eff_traffic_level = "LOW"
        elif shipping_mode == "RAIL":
            eff_dist = route["distance_km"] * 0.95
            eff_traffic_min = (eff_dist / 46.0) * 60.0 + 360.0

        predictions = predict_all(
            distance_km          = eff_dist,
            traffic_duration_min = eff_traffic_min,
            traffic_level        = eff_traffic_level,
            package_weight_kg    = weight,
            package_type         = pkg_type,
            priority             = priority,
            shipping_mode        = shipping_mode,
        )
        # Overall ensemble for the full route
        full_ensemble = predict_ensemble(
            distance_km          = eff_dist,
            traffic_duration_min = eff_traffic_min,
            traffic_level        = eff_traffic_level,
            package_weight_kg    = weight,
            package_type         = pkg_type,
            priority             = priority,
            shipping_mode        = shipping_mode,
        )
        predictions["ensemble_hours"]   = full_ensemble["ensemble_hours"]
        predictions["dominant_model"]   = full_ensemble["dominant_model"]
        predictions["model_weights"]    = full_ensemble["model_weights"]
        # Ensure min and max bounds for delivery window
        model_preds = [v for v in [predictions.get("xgboost"), predictions.get("random_forest"), predictions.get("linear_regression")] if v is not None]
        min_hours = min(model_preds) if model_preds else predictions["recommended_hours"]
        max_hours = max(model_preds) if model_preds else predictions["recommended_hours"]
        predictions["min_hours"] = round(min_hours, 3)
        predictions["max_hours"] = round(max_hours, 3)
        predictions["confidence_low"] = round(min_hours, 3)
        predictions["confidence_high"] = round(max_hours, 3)
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 503

    # ── Step 3b: 25 km Segmented Per-Leg Transit & Weather ──
    sampled_wps = route.get("sampled_waypoints", [])
    segments = []
    total_segmented_hours = 0.0

    if len(sampled_wps) > 1:
        total_d = route["distance_km"] or 1.0
        total_rec_hours = predictions["recommended_hours"] or 1.0

        weather_multipliers = {
            "STORM": 1.25,
            "HEAVY_RAIN": 1.15,
            "SNOW": 1.15,
            "RAIN": 1.08,
            "FOG": 1.08,
            "CLOUDY": 1.0,
            "CLEAR": 1.0,
        }

        # Pre-fetch weather only for major ~50km checkpoints in parallel for sub-second API speed
        major_wps = [wp for wp in sampled_wps if wp.get("is_major_marker")]
        if not major_wps:
            major_wps = [sampled_wps[0], sampled_wps[-1]]

        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=5) as executor:
            major_weathers = list(executor.map(
                lambda wp: get_weather_by_coords(wp["lat"], wp["lon"], wp["name"]),
                major_wps
            ))

        # Helper to get nearest major checkpoint weather for any 25 km waypoint
        def get_nearest_leg_weather(wp):
            best_w = major_weathers[0]
            min_d = float("inf")
            for m_wp, m_w in zip(major_wps, major_weathers):
                d = abs(wp["km_offset"] - m_wp["km_offset"])
                if d < min_d:
                    min_d = d
                    best_w = m_w
            return best_w

        for i in range(1, len(sampled_wps)):
            wp_prev = sampled_wps[i - 1]
            wp_curr = sampled_wps[i]
            leg_dist = round(wp_curr["km_offset"] - wp_prev["km_offset"], 1)
            if leg_dist <= 0:
                leg_dist = round(total_d / (len(sampled_wps) - 1), 1)

            leg_weather = get_nearest_leg_weather(wp_curr)
            cond = leg_weather.get("weather_condition", "CLEAR")
            w_mult = weather_multipliers.get(cond, 1.0)

            # Proportional share of the trip represented by this leg
            leg_share = leg_dist / total_d

            # Allocate trip delivery duration proportionally and apply local weather impact
            leg_hours = round(total_rec_hours * leg_share * w_mult, 3)
            total_segmented_hours += leg_hours

            # Per-model hours on this leg
            leg_model_hours = {}
            for m_name in ["xgboost", "random_forest", "linear_regression"]:
                m_val = predictions.get(m_name)
                if m_val is not None:
                    leg_model_hours[m_name] = round(m_val * leg_share * w_mult, 3)

            segments.append({
                "leg": i,
                "heading": f"{wp_prev['name']} -> {wp_curr['name']}",
                "corridor_leg": f"{wp_prev['name']} -> {wp_curr['name']}",
                "start_name": wp_prev["name"],
                "end_name": wp_curr["name"],
                "start_coords": [wp_prev["lat"], wp_prev["lon"]],
                "end_coords": [wp_curr["lat"], wp_curr["lon"]],
                "distance_km": leg_dist,
                "predicted_hours": leg_hours,
                "dominant_model": predictions.get("dominant_model", "xgboost"),
                "model_hours": leg_model_hours,
                "model_weights": predictions.get("model_weights", {}),
                "weather": leg_weather,
            })

        total_segmented_hours = round(total_segmented_hours, 2)
        predictions["segmented_sum_hours"] = total_segmented_hours

    # ── Step 3c: SLM Model Routing (Route, Weather & Leg Distances) ──
    try:
        from models.slm_router import decide_model_with_slm
        slm_decision = decide_model_with_slm(
            origin            = origin,
            destination       = destination,
            distance_km       = route["distance_km"],
            traffic_level     = route["traffic_level"],
            weather_condition = weather["weather_condition"],
            weather_data      = weather,
            legs              = segments,
            available_models  = list(predictions.get("all_models", {}).keys()),
        )
        # Apply SLM chosen model if available
        chosen_slm_model = slm_decision.get("chosen_model")
        if chosen_slm_model and chosen_slm_model in predictions.get("all_models", {}):
            predictions["recommended_model"] = chosen_slm_model
            predictions["recommended_hours"] = predictions["all_models"][chosen_slm_model]
    except Exception as e:
        logger.warning("SLM router failed: %s", e)
        slm_decision = {
            "chosen_model": predictions.get("recommended_model", "voting"),
            "reason": "Standard distance-tier model assignment.",
            "source": "DeliverAI Baseline",
            "leg_assignments": [],
        }

    # ── Explainable AI (XAI) & Carbon Footprint ──────────────
    try:
        explanation = explain_prediction(
            distance_km          = route["distance_km"],
            traffic_duration_min = route["traffic_duration_min"],
            traffic_level        = route["traffic_level"],
            package_weight_kg    = weight,
            package_type         = pkg_type,
            priority             = priority,
            shipping_mode        = shipping_mode,
        )
    except Exception as e:
        logger.warning("Explain prediction failed: %s", e)
        explanation = {"base_hours": 10.0, "factors": [], "summary": "Attribution model unavailable."}

    sustainability = calculate_carbon_footprint(
        distance_km       = route["distance_km"],
        package_weight_kg = weight,
        shipping_mode     = shipping_mode,
    )

    # ── Multi-Modal Rail & Airways Direct Scan ────────────────
    try:
        multimodal_options = check_multimodal_options(
            origin           = origin,
            destination      = destination,
            origin_coords    = route.get("origin_coords"),
            dest_coords      = route.get("destination_coords") or route.get("dest_coords"),
            road_distance_km = route.get("distance_km"),
            road_hours       = predictions.get("recommended_hours"),
            weight_kg        = weight,
        )
    except Exception as e:
        logger.warning("Multimodal options scan failed: %s", e)
        multimodal_options = None

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
            "geometry":             route.get("geometry", []),
            "sampled_waypoints":    route.get("sampled_waypoints", []),
        },
        "weather": {
            "condition":           weather["weather_condition"],
            "temperature_celsius": weather["temperature_celsius"],
            "wind_speed_kmh":      weather["wind_speed_kmh"],
            "precipitation_mm":    weather["precipitation_mm"],
            "description":         weather.get("description", ""),
            "checkpoints":         weather.get("checkpoints", {}),
        },
        "segments": segments,
        "total_segmented_hours": total_segmented_hours,
        "package": {
            "weight_kg":     weight,
            "type":          pkg_type,
            "priority":      priority,
            "shipping_mode": shipping_mode,
        },
        "predictions": predictions,
        "slm_router": slm_decision,
        "explanation": explanation,
        "sustainability": sustainability,
        "multimodal_options": multimodal_options,
        "response_time_ms": response_ms,
    }), 200


@predict_bp.route("/routes/modal-availability", methods=["GET"])
def modal_availability():
    """
    GET /api/routes/modal-availability?origin=Mumbai&destination=Pune&weight=5.0
    Quick endpoint that scans Indian Railway network & commercial aviation hubs
    to detect direct Rail and Air options between any origin and destination.
    """
    origin = request.args.get("origin", "").strip()
    destination = request.args.get("destination", "").strip()
    if not origin or not destination:
        return jsonify({"error": "origin and destination are required"}), 400

    try:
        weight = float(request.args.get("weight", 5.0))
    except (ValueError, TypeError):
        weight = 5.0

    try:
        route = get_route_info(origin, destination)
        options = check_multimodal_options(
            origin           = origin,
            destination      = destination,
            origin_coords    = route.get("origin_coords"),
            dest_coords      = route.get("destination_coords") or route.get("dest_coords"),
            road_distance_km = route.get("distance_km"),
            weight_kg        = weight,
        )
        return jsonify(options)
    except Exception as e:
        logger.debug("Fast route fallback in modal_availability: %s", e)
        options = check_multimodal_options(
            origin      = origin,
            destination = destination,
            weight_kg   = weight,
        )
        return jsonify(options)


@predict_bp.route("/predict/what-if", methods=["POST"])
def what_if():
    """Fast sub-second simulation endpoint to test hypothetical traffic, priority, or shipping mode."""

    data = request.get_json(force=True, silent=True) or {}
    try:
        dist = float(data.get("distance_km", 100.0))
        traffic_min = float(data.get("traffic_duration_min", 90.0))
        traffic_lvl = str(data.get("traffic_level", "MODERATE")).upper()
        weight = float(data.get("package_weight_kg", 5.0))
        pkg_type = str(data.get("package_type", "MEDIUM")).upper()
        priority = str(data.get("priority", "STANDARD")).upper()
        shipping_mode = str(data.get("shipping_mode", "ROAD")).upper()

        if data.get("recalc_traffic"):
            traffic_factors = {"LOW": 1.0, "MODERATE": 1.2, "HIGH": 1.5, "SEVERE": 2.0}
            base_min = dist * 1.0
            traffic_min = base_min * traffic_factors.get(traffic_lvl, 1.2)

        preds = predict_all(
            distance_km          = dist,
            traffic_duration_min = traffic_min,
            traffic_level        = traffic_lvl,
            package_weight_kg    = weight,
            package_type         = pkg_type,
            priority             = priority,
            shipping_mode        = shipping_mode,
        )
        full_ensemble = predict_ensemble(
            distance_km          = dist,
            traffic_duration_min = traffic_min,
            traffic_level        = traffic_lvl,
            package_weight_kg    = weight,
            package_type         = pkg_type,
            priority             = priority,
            shipping_mode        = shipping_mode,
        )
        preds["ensemble_hours"] = full_ensemble["ensemble_hours"]
        preds["dominant_model"] = full_ensemble["dominant_model"]
        preds["model_weights"]  = full_ensemble["model_weights"]

        model_preds = [v for v in [preds.get("xgboost"), preds.get("random_forest"), preds.get("linear_regression")] if v is not None]
        preds["min_hours"] = round(min(model_preds) if model_preds else preds["recommended_hours"], 3)
        preds["max_hours"] = round(max(model_preds) if model_preds else preds["recommended_hours"], 3)
        preds["confidence_low"] = preds["min_hours"]
        preds["confidence_high"] = preds["max_hours"]

        explanation = explain_prediction(
            distance_km          = dist,
            traffic_duration_min = traffic_min,
            traffic_level        = traffic_lvl,
            package_weight_kg    = weight,
            package_type         = pkg_type,
            priority             = priority,
            shipping_mode        = shipping_mode,
        )
        sustainability = calculate_carbon_footprint(
            distance_km       = dist,
            package_weight_kg = weight,
            shipping_mode     = shipping_mode,
        )

        return jsonify({
            "predictions": preds,
            "explanation": explanation,
            "sustainability": sustainability,
            "traffic_duration_min": round(traffic_min, 1),
            "traffic_level": traffic_lvl,
        }), 200
    except Exception as e:
        logger.error("What-if simulation error: %s", e)
        return jsonify({"error": str(e)}), 400

