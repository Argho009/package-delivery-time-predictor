"""
routes/analytics.py — Aggregated analytics endpoints
GET /api/analytics/summary          — high-level KPIs
GET /api/analytics/model-comparison — ML metrics for all 3 models
GET /api/analytics/traffic-impact   — avg delivery time by traffic level
GET /api/analytics/weather-impact   — avg delivery time by weather condition
GET /api/analytics/predictions/recent — last 50 prediction logs
"""

from flask import Blueprint, jsonify, request
from sqlalchemy import func

from database.db import db
from database.models import DeliveryRecord, PredictionLog, ModelMetric
from models.predict import get_metrics, get_best_model

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


@analytics_bp.route("/summary", methods=["GET"])
def summary():
    """High-level KPI dashboard stats."""
    total_records    = DeliveryRecord.query.count()
    total_predictions = PredictionLog.query.count()

    avg_time_row = db.session.query(
        func.avg(DeliveryRecord.actual_time_hours)
    ).scalar()
    avg_time = round(float(avg_time_row), 3) if avg_time_row else 0.0

    avg_distance_row = db.session.query(
        func.avg(DeliveryRecord.distance_km)
    ).scalar()
    avg_distance = round(float(avg_distance_row), 2) if avg_distance_row else 0.0

    # Avg prediction error (MAE from stored records)
    error_row = db.session.query(
        func.avg(func.abs(
            DeliveryRecord.predicted_time_hours - DeliveryRecord.actual_time_hours
        ))
    ).filter(
        DeliveryRecord.predicted_time_hours.isnot(None),
        DeliveryRecord.actual_time_hours.isnot(None),
    ).scalar()
    avg_error = round(float(error_row), 3) if error_row else 0.0

    best_model = get_best_model()

    return jsonify({
        "total_delivery_records": total_records,
        "total_predictions_made": total_predictions,
        "avg_delivery_time_hours": avg_time,
        "avg_route_distance_km":   avg_distance,
        "avg_prediction_error_hours": avg_error,
        "best_model": best_model,
    }), 200


@analytics_bp.route("/model-comparison", methods=["GET"])
def model_comparison():
    """Current ML model metrics for all 3 models."""
    db_metrics = ModelMetric.query.filter_by(is_current=True).all()
    mem_metrics = get_metrics()

    result = {}
    for m in db_metrics:
        result[m.model_name] = {
            "rmse":       m.rmse,
            "mae":        m.mae,
            "r2":         m.r2,
            "trained_on": m.trained_on,
            "trained_at": m.trained_at.isoformat() if m.trained_at else None,
        }

    # Fall back to in-memory metrics if DB empty
    if not result and mem_metrics:
        result = mem_metrics

    return jsonify({
        "models":      result,
        "best_model":  get_best_model(),
    }), 200


@analytics_bp.route("/traffic-impact", methods=["GET"])
def traffic_impact():
    """Average delivery time grouped by traffic level."""
    rows = db.session.query(
        DeliveryRecord.traffic_level,
        func.avg(DeliveryRecord.actual_time_hours).label("avg_hours"),
        func.count(DeliveryRecord.id).label("count"),
    ).filter(
        DeliveryRecord.actual_time_hours.isnot(None)
    ).group_by(DeliveryRecord.traffic_level).all()

    return jsonify([
        {
            "traffic_level": r.traffic_level,
            "avg_hours":     round(float(r.avg_hours), 3),
            "count":         r.count,
        } for r in rows
    ]), 200


@analytics_bp.route("/weather-impact", methods=["GET"])
def weather_impact():
    """Average delivery time grouped by weather condition."""
    rows = db.session.query(
        DeliveryRecord.weather_condition,
        func.avg(DeliveryRecord.actual_time_hours).label("avg_hours"),
        func.count(DeliveryRecord.id).label("count"),
    ).filter(
        DeliveryRecord.actual_time_hours.isnot(None)
    ).group_by(DeliveryRecord.weather_condition).all()

    return jsonify([
        {
            "weather_condition": r.weather_condition,
            "avg_hours":        round(float(r.avg_hours), 3),
            "count":            r.count,
        } for r in rows
    ]), 200


@analytics_bp.route("/predictions/recent", methods=["GET"])
def recent_predictions():
    """Last N prediction logs."""
    n    = min(request.args.get("n", 50, type=int), 200)
    logs = PredictionLog.query.order_by(
        PredictionLog.created_at.desc()).limit(n).all()
    return jsonify([log.to_dict() for log in logs]), 200
