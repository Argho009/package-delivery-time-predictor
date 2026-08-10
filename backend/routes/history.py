"""
routes/history.py — Delivery records CRUD
GET  /api/history       — paginated list
POST /api/history       — log a completed delivery
GET  /api/history/<id>  — single record
"""

import random
import string
from datetime import datetime
from flask import Blueprint, request, jsonify

from database.db import db
from database.models import DeliveryRecord

history_bp = Blueprint("history", __name__, url_prefix="/api")


def _gen_tracking_id():
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"PKG{suffix}"


@history_bp.route("/history", methods=["GET"])
def list_history():
    """
    GET /api/history?page=1&per_page=20&traffic=HIGH&weather=RAIN&priority=EXPRESS
    """
    page     = request.args.get("page",     1,   type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)

    query = DeliveryRecord.query

    # Filters
    if tf := request.args.get("traffic"):
        query = query.filter(DeliveryRecord.traffic_level == tf.upper())
    if wf := request.args.get("weather"):
        query = query.filter(DeliveryRecord.weather_condition == wf.upper())
    if pf := request.args.get("priority"):
        query = query.filter(DeliveryRecord.priority == pf.upper())
    if origin := request.args.get("origin"):
        query = query.filter(DeliveryRecord.origin_city.ilike(f"%{origin}%"))
    if dest := request.args.get("destination"):
        query = query.filter(DeliveryRecord.destination_city.ilike(f"%{dest}%"))

    query = query.order_by(DeliveryRecord.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "data":       [r.to_dict() for r in pagination.items],
        "total":      pagination.total,
        "page":       page,
        "per_page":   per_page,
        "total_pages": pagination.pages,
    }), 200


@history_bp.route("/history/<int:record_id>", methods=["GET"])
def get_record(record_id):
    record = DeliveryRecord.query.get_or_404(record_id)
    return jsonify(record.to_dict()), 200


@history_bp.route("/history", methods=["POST"])
def create_record():
    """Log a completed delivery (with actual_time_hours)."""
    data = request.get_json(force=True, silent=True) or {}

    required = [
        "origin_city", "destination_city", "distance_km",
        "traffic_duration_min", "traffic_level", "weather_condition",
        "package_weight_kg", "package_type", "priority", "actual_time_hours"
    ]
    missing = [f for f in required if data.get(f) is None]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    record = DeliveryRecord(
        tracking_id          = _gen_tracking_id(),
        origin_city          = data["origin_city"],
        destination_city     = data["destination_city"],
        distance_km          = float(data["distance_km"]),
        base_duration_min    = float(data.get("base_duration_min", data["distance_km"] / 60 * 60)),
        traffic_duration_min = float(data["traffic_duration_min"]),
        traffic_level        = data["traffic_level"].upper(),
        weather_condition    = data["weather_condition"].upper(),
        temperature_celsius  = data.get("temperature_celsius"),
        wind_speed_kmh       = data.get("wind_speed_kmh"),
        precipitation_mm     = data.get("precipitation_mm", 0.0),
        package_weight_kg    = float(data["package_weight_kg"]),
        package_type         = data["package_type"].upper(),
        priority             = data["priority"].upper(),
        predicted_time_hours = data.get("predicted_time_hours"),
        actual_time_hours    = float(data["actual_time_hours"]),
        model_used           = data.get("model_used"),
        delivered_at         = datetime.utcnow(),
    )
    db.session.add(record)
    db.session.commit()

    return jsonify(record.to_dict()), 201
