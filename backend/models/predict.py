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

    recommended = _best_model if _best_model in results else next(iter(results))
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
