"""
models/predict.py — Load saved models and run inference.
Models are loaded once on import (singleton pattern).
Updated for no-weather feature set.
"""

import os
import json
import logging
import numpy as np
import joblib

from utils.feature_engineering import build_feature_vector

logger = logging.getLogger(__name__)

SAVED_DIR = os.path.join(os.path.dirname(__file__), "saved")

_models: dict  = {}
_scaler        = None
_metrics: dict = {}
_best_model    = "xgboost"
_importances: dict = {}


def _load_models():
    global _models, _scaler, _metrics, _best_model, _importances

    model_files = {
        "xgboost":           "xgboost.pkl",
        "random_forest":     "random_forest.pkl",
        "linear_regression": "linear_regression.pkl",
    }

    for name, fname in model_files.items():
        path = os.path.join(SAVED_DIR, fname)
        if os.path.exists(path):
            _models[name] = joblib.load(path)
            logger.info("Loaded model: %s", name)
        else:
            logger.warning("Model not found: %s (run models/train.py)", path)

    scaler_path = os.path.join(SAVED_DIR, "scaler.pkl")
    if os.path.exists(scaler_path):
        _scaler = joblib.load(scaler_path)

    metrics_path = os.path.join(SAVED_DIR, "metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path) as f:
            data = json.load(f)
            _metrics      = data.get("metrics", {})
            _best_model   = data.get("best_model", "xgboost")
            _importances  = data.get("feature_importances", {})


_load_models()


_range_model_cache = {}

def _load_range_performance():
    global _range_model_cache
    try:
        import csv
        models_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(os.path.dirname(models_dir))
        csv_path = os.path.join(root_dir, "range_performance_1km.csv")
        
        if os.path.exists(csv_path):
            with open(csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    tier = row.get("Distance Tier (km)")
                    model = row.get("Dominant Model")
                    if tier and model:
                        parts = tier.split("-")
                        if len(parts) == 2:
                            try:
                                start_km = float(parts[0])
                                end_km = float(parts[1])
                                _range_model_cache[(start_km, end_km)] = model.strip().lower()
                            except ValueError:
                                pass
            logger.info("Loaded 1km range model configurations from range_performance_1km.csv")
    except Exception as e:
        logger.warning("Failed to load range_performance_1km.csv: %s", e)

_load_range_performance()


def get_recommended_model_for_distance(distance_km: float) -> str:
    """Find the best model from 1 km binned performance, using nearest-bin matching to maximize accuracy."""
    if not _range_model_cache:
        return _best_model or "xgboost"

    # 1. Try exact match first
    for (start, end), model in _range_model_cache.items():
        if start <= distance_km < end:
            return model

    # 2. Find the nearest bin by distance to bin center
    best_model = None
    min_dist = float("inf")
    for (start, end), model in _range_model_cache.items():
        bin_center = (start + end) / 2.0
        d = abs(distance_km - bin_center)
        if d < min_dist:
            min_dist = d
            best_model = model

    return best_model or _best_model or "xgboost"


def models_available() -> list:
    return list(_models.keys())

def get_metrics() -> dict:
    return _metrics

def get_best_model() -> str:
    return _best_model

def get_feature_importances() -> dict:
    return _importances


def predict_all(
    distance_km: float,
    traffic_duration_min: float,
    traffic_level: str,
    package_weight_kg: float,
    package_type: str,
    priority: str,
    shipping_mode: str = "ROAD",
) -> dict:
    """
    Run prediction with all loaded models.

    Returns:
        {
            "xgboost":           float | None,
            "random_forest":     float | None,
            "linear_regression": float | None,
            "recommended_model": str,
            "recommended_hours": float,
            "confidence_low":    float,
            "confidence_high":   float,
        }
    """
    if not _models:
        raise RuntimeError(
            "No models loaded. Run 'python -m models.train' first.")

    X = build_feature_vector(
        distance_km, traffic_duration_min, traffic_level,
        package_weight_kg, package_type, priority, shipping_mode,
    )

    results = {}
    for name, model in _models.items():
        try:
            X_input = _scaler.transform(X) if name == "linear_regression" and _scaler else X
            pred = float(model.predict(X_input)[0])
            results[name] = round(max(pred, 0.1), 3)
        except Exception as e:
            logger.error("Prediction failed for %s: %s", name, e)
            results[name] = None

    recommended = get_recommended_model_for_distance(distance_km)
    if recommended not in results or results[recommended] is None:
        recommended = _best_model if _best_model in results and results[_best_model] is not None else next(
            (k for k, v in results.items() if v is not None), "xgboost"
        )
    rec_hours   = results.get(recommended)
    rmse        = _metrics.get(recommended, {}).get("rmse", 0.5) if _metrics else 0.5

    return {
        "xgboost":           results.get("xgboost"),
        "random_forest":     results.get("random_forest"),
        "linear_regression": results.get("linear_regression"),
        "recommended_model": recommended,
        "recommended_hours": rec_hours,
        "confidence_low":    round(max((rec_hours or 0) - rmse, 0.1), 3),
        "confidence_high":   round((rec_hours or 0) + rmse, 3),
    }


def predict_ensemble(
    distance_km: float,
    traffic_duration_min: float,
    traffic_level: str,
    package_weight_kg: float,
    package_type: str,
    priority: str,
    shipping_mode: str = "ROAD",
) -> dict:
    """
    Run all loaded models and return an inverse-RMSE weighted ensemble prediction.
    Models with lower training RMSE contribute more to the final answer.

    Returns:
        {
            "ensemble_hours":    float,   # weighted average of all models
            "dominant_model":    str,     # model with highest weight
            "model_hours": {              # per-model raw predictions
                "xgboost": float,
                "random_forest": float,
                "linear_regression": float
            },
            "model_weights": {            # normalised weight per model
                "xgboost": float, ...
            }
        }
    """
    if not _models:
        raise RuntimeError("No models loaded. Run 'python -m models.train' first.")

    X = build_feature_vector(
        distance_km, traffic_duration_min, traffic_level,
        package_weight_kg, package_type, priority, shipping_mode,
    )

    raw_preds = {}
    for name, model in _models.items():
        try:
            X_input = _scaler.transform(X) if name == "linear_regression" and _scaler else X
            pred = float(model.predict(X_input)[0])
            raw_preds[name] = round(max(pred, 0.1), 3)
        except Exception as e:
            logger.error("Ensemble prediction failed for %s: %s", name, e)

    if not raw_preds:
        raise RuntimeError("All models failed during ensemble prediction.")

    # Compute inverse-RMSE weights: better model (lower RMSE) → higher weight
    inv_weights = {}
    for name in raw_preds:
        rmse = _metrics.get(name, {}).get("rmse", 1.0) if _metrics else 1.0
        inv_weights[name] = 1.0 / max(rmse, 1e-6)

    total_weight = sum(inv_weights.values())
    norm_weights = {k: v / total_weight for k, v in inv_weights.items()}

    ensemble_hours = sum(raw_preds[k] * norm_weights[k] for k in raw_preds)
    dominant_model = get_recommended_model_for_distance(distance_km)
    if dominant_model not in raw_preds or raw_preds[dominant_model] is None:
        dominant_model = max(norm_weights, key=norm_weights.get) if norm_weights else "xgboost"

    return {
        "ensemble_hours": round(ensemble_hours, 3),
        "dominant_model": dominant_model,
        "model_hours":    raw_preds,
        "model_weights":  {k: round(v, 4) for k, v in norm_weights.items()},
    }
