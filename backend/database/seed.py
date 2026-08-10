"""
database/seed.py — Generate and insert 1200+ synthetic delivery records
Run once: python -m database.seed  (from the backend/ directory)
"""

import sys
import os
import random
import math
from datetime import datetime, timedelta

# Allow running from backend/ directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from database.db import db
from database.models import DeliveryRecord

# ── Synthetic city data (city, lat, lng) ─────────────────────────
CITIES = [
    ("Mumbai",    19.0760, 72.8777),
    ("Delhi",     28.6139, 77.2090),
    ("Bangalore", 12.9716, 77.5946),
    ("Hyderabad", 17.3850, 78.4867),
    ("Chennai",   13.0827, 80.2707),
    ("Kolkata",   22.5726, 88.3639),
    ("Pune",      18.5204, 73.8567),
    ("Ahmedabad", 23.0225, 72.5714),
    ("Jaipur",    26.9124, 75.7873),
    ("Surat",     21.1702, 72.8311),
    ("Lucknow",   26.8467, 80.9462),
    ("Kanpur",    26.4499, 80.3319),
    ("Nagpur",    21.1458, 79.0882),
    ("Indore",    22.7196, 75.8577),
    ("Bhopal",    23.2599, 77.4126),
    ("Visakhapatnam", 17.6868, 83.2185),
    ("Patna",     25.5941, 85.1376),
    ("Vadodara",  22.3072, 73.1812),
    ("Ghaziabad", 28.6692, 77.4538),
    ("Coimbatore",11.0168, 76.9558),
]

TRAFFIC_LEVELS = ["LOW", "MODERATE", "HIGH", "SEVERE"]
TRAFFIC_WEIGHTS = [0.25, 0.40, 0.25, 0.10]

WEATHER_CONDITIONS = ["CLEAR", "CLOUDY", "RAIN", "HEAVY_RAIN", "SNOW", "FOG", "STORM"]
WEATHER_WEIGHTS    = [0.35, 0.25, 0.20, 0.07, 0.03, 0.07, 0.03]

PACKAGE_TYPES     = ["SMALL", "MEDIUM", "LARGE", "FRAGILE", "PERISHABLE"]
PACKAGE_WEIGHTS   = {
    "SMALL":      (0.1, 2.0),
    "MEDIUM":     (2.0, 10.0),
    "LARGE":      (10.0, 50.0),
    "FRAGILE":    (0.5, 5.0),
    "PERISHABLE": (0.5, 15.0),
}

PRIORITIES = ["STANDARD", "EXPRESS", "OVERNIGHT"]
PRIORITY_WEIGHTS = [0.60, 0.30, 0.10]

# Traffic multipliers on base duration
TRAFFIC_MULTIPLIER = {"LOW": 1.05, "MODERATE": 1.30, "HIGH": 1.65, "SEVERE": 2.10}

# Weather delay (extra hours)
WEATHER_DELAY = {
    "CLEAR": 0.0, "CLOUDY": 0.05, "RAIN": 0.25, "HEAVY_RAIN": 0.60,
    "SNOW": 1.0, "FOG": 0.40, "STORM": 1.5
}

# Priority speed factors (multiplied on final time)
PRIORITY_FACTOR = {"STANDARD": 1.0, "EXPRESS": 0.75, "OVERNIGHT": 0.50}


def haversine_km(lat1, lng1, lat2, lng2):
    """Great-circle distance between two coordinates."""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def compute_delivery_time(distance_km, traffic_level, weather_condition,
                          package_weight_kg, package_type, priority):
    """Simulate realistic delivery time in hours with added noise."""
    # Base: average 60 km/h commercial speed
    base_hours = distance_km / 60.0

    # Traffic delay
    traffic_factor = TRAFFIC_MULTIPLIER[traffic_level]
    traffic_hours = base_hours * traffic_factor

    # Weather delay
    weather_extra = WEATHER_DELAY[weather_condition]

    # Weight penalty (heavier = more loading time)
    weight_penalty = package_weight_kg * 0.02

    # Fragile/perishable handling
    handling = 0.3 if package_type in ("FRAGILE", "PERISHABLE") else 0.0

    # Priority boost
    priority_mult = PRIORITY_FACTOR[priority]

    total = (traffic_hours + weather_extra + weight_penalty + handling) * priority_mult

    # Add realistic noise (±15%)
    noise = random.uniform(0.85, 1.15)
    return round(total * noise, 3)


def generate_tracking_id():
    import random, string
    prefix = "PKG"
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"{prefix}{suffix}"


def seed(n: int = 1200):
    app = create_app()
    with app.app_context():
        db.create_all()

        existing = DeliveryRecord.query.count()
        if existing >= n:
            print(f"[seed] Already have {existing} records. Skipping.")
            return

        records = []
        start_date = datetime.utcnow() - timedelta(days=365)

        for i in range(n - existing):
            # Pick random origin & destination (different cities)
            origin, dest = random.sample(CITIES, 2)
            o_name, o_lat, o_lng = origin
            d_name, d_lat, d_lng = dest

            distance = round(haversine_km(o_lat, o_lng, d_lat, d_lng), 2)
            base_dur = round(distance / 60.0 * 60, 1)   # minutes

            traffic_level = random.choices(TRAFFIC_LEVELS, TRAFFIC_WEIGHTS)[0]
            traffic_dur   = round(base_dur * TRAFFIC_MULTIPLIER[traffic_level], 1)

            weather       = random.choices(WEATHER_CONDITIONS, WEATHER_WEIGHTS)[0]
            temperature   = round(random.uniform(5, 42), 1)
            wind_speed    = round(random.uniform(0, 60), 1)
            precipitation = round(random.uniform(0, 50) if weather in
                                  ("RAIN","HEAVY_RAIN","STORM") else 0, 1)

            pkg_type  = random.choice(PACKAGE_TYPES)
            wt_min, wt_max = PACKAGE_WEIGHTS[pkg_type]
            weight    = round(random.uniform(wt_min, wt_max), 2)

            priority  = random.choices(PRIORITIES, PRIORITY_WEIGHTS)[0]

            actual_time = compute_delivery_time(
                distance, traffic_level, weather, weight, pkg_type, priority)

            # Predicted time ≈ actual ± small delta (simulating earlier prediction)
            predicted_time = round(actual_time * random.uniform(0.92, 1.08), 3)

            created = start_date + timedelta(
                seconds=random.randint(0, 365 * 24 * 3600))
            delivered = created + timedelta(hours=actual_time)

            record = DeliveryRecord(
                tracking_id          = generate_tracking_id(),
                origin_city          = o_name,
                destination_city     = d_name,
                origin_lat           = o_lat,
                origin_lng           = o_lng,
                destination_lat      = d_lat,
                destination_lng      = d_lng,
                distance_km          = distance,
                base_duration_min    = base_dur,
                traffic_duration_min = traffic_dur,
                traffic_level        = traffic_level,
                weather_condition    = weather,
                temperature_celsius  = temperature,
                wind_speed_kmh       = wind_speed,
                precipitation_mm     = precipitation,
                package_weight_kg    = weight,
                package_type         = pkg_type,
                priority             = priority,
                predicted_time_hours = predicted_time,
                actual_time_hours    = actual_time,
                model_used           = random.choice(["xgboost","random_forest","linear_regression"]),
                created_at           = created,
                delivered_at         = delivered,
            )
            records.append(record)

            if (i + 1) % 100 == 0:
                db.session.bulk_save_objects(records)
                db.session.commit()
                records = []
                print(f"[seed] Inserted {i + 1} records...")

        if records:
            db.session.bulk_save_objects(records)
            db.session.commit()

        total = DeliveryRecord.query.count()
        print(f"[seed] Done! Total records in DB: {total}")


if __name__ == "__main__":
    seed()
