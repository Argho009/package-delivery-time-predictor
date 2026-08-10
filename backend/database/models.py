"""
database/models.py — SQLAlchemy ORM models
"""

from datetime import datetime
from database.db import db


class DeliveryRecord(db.Model):
    """Historical and completed delivery records (used for ML training)."""
    __tablename__ = "delivery_records"

    id                   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tracking_id          = db.Column(db.String(20), unique=True, nullable=False)
    origin_city          = db.Column(db.String(100), nullable=False)
    destination_city     = db.Column(db.String(100), nullable=False)
    origin_lat           = db.Column(db.Float)
    origin_lng           = db.Column(db.Float)
    destination_lat      = db.Column(db.Float)
    destination_lng      = db.Column(db.Float)
    distance_km          = db.Column(db.Float, nullable=False)
    base_duration_min    = db.Column(db.Float, nullable=False)
    traffic_duration_min = db.Column(db.Float, nullable=False)
    traffic_level        = db.Column(db.Enum("LOW","MODERATE","HIGH","SEVERE"), nullable=False)
    weather_condition    = db.Column(db.Enum("CLEAR","CLOUDY","RAIN","HEAVY_RAIN","SNOW","FOG","STORM"), nullable=False)
    temperature_celsius  = db.Column(db.Float)
    wind_speed_kmh       = db.Column(db.Float)
    precipitation_mm     = db.Column(db.Float, default=0.0)
    package_weight_kg    = db.Column(db.Float, nullable=False)
    package_type         = db.Column(db.Enum("SMALL","MEDIUM","LARGE","FRAGILE","PERISHABLE"), nullable=False)
    priority             = db.Column(db.Enum("STANDARD","EXPRESS","OVERNIGHT"), nullable=False)
    predicted_time_hours = db.Column(db.Float)
    actual_time_hours    = db.Column(db.Float)
    model_used           = db.Column(db.String(30))
    created_at           = db.Column(db.DateTime, default=datetime.utcnow)
    delivered_at         = db.Column(db.DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "tracking_id": self.tracking_id,
            "origin_city": self.origin_city,
            "destination_city": self.destination_city,
            "distance_km": self.distance_km,
            "traffic_level": self.traffic_level,
            "weather_condition": self.weather_condition,
            "package_weight_kg": self.package_weight_kg,
            "package_type": self.package_type,
            "priority": self.priority,
            "predicted_time_hours": self.predicted_time_hours,
            "actual_time_hours": self.actual_time_hours,
            "model_used": self.model_used,
            "prediction_error": round(abs((self.predicted_time_hours or 0) - (self.actual_time_hours or 0)), 3)
                                if self.predicted_time_hours and self.actual_time_hours else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
        }


class PredictionLog(db.Model):
    """Log of every real-time prediction request."""
    __tablename__ = "prediction_logs"

    id                   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id           = db.Column(db.String(36), nullable=False)
    origin               = db.Column(db.String(255), nullable=False)
    destination          = db.Column(db.String(255), nullable=False)
    distance_km          = db.Column(db.Float)
    traffic_duration_min = db.Column(db.Float)
    traffic_level        = db.Column(db.String(20))
    weather_condition    = db.Column(db.String(30))
    temperature_celsius  = db.Column(db.Float)
    wind_speed_kmh       = db.Column(db.Float)
    precipitation_mm     = db.Column(db.Float)
    package_weight_kg    = db.Column(db.Float)
    package_type         = db.Column(db.String(20))
    priority             = db.Column(db.String(20))
    predicted_xgboost    = db.Column(db.Float)
    predicted_rf         = db.Column(db.Float)
    predicted_lr         = db.Column(db.Float)
    recommended_model    = db.Column(db.String(30))
    recommended_hours    = db.Column(db.Float)
    api_response_ms      = db.Column(db.Integer)
    created_at           = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "request_id": self.request_id,
            "origin": self.origin,
            "destination": self.destination,
            "distance_km": self.distance_km,
            "traffic_level": self.traffic_level,
            "weather_condition": self.weather_condition,
            "package_weight_kg": self.package_weight_kg,
            "package_type": self.package_type,
            "priority": self.priority,
            "predictions": {
                "xgboost": self.predicted_xgboost,
                "random_forest": self.predicted_rf,
                "linear_regression": self.predicted_lr,
            },
            "recommended_model": self.recommended_model,
            "recommended_hours": self.recommended_hours,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ModelMetric(db.Model):
    """Stores evaluation metrics for each trained model."""
    __tablename__ = "model_metrics"

    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    model_name = db.Column(db.String(30), nullable=False)
    rmse       = db.Column(db.Float, nullable=False)
    mae        = db.Column(db.Float, nullable=False)
    r2         = db.Column(db.Float, nullable=False)
    trained_on = db.Column(db.Integer, nullable=False)
    trained_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_current = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "model_name": self.model_name,
            "rmse": self.rmse,
            "mae": self.mae,
            "r2": self.r2,
            "trained_on": self.trained_on,
            "trained_at": self.trained_at.isoformat() if self.trained_at else None,
        }
