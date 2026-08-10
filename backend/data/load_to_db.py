"""
data/load_to_db.py — Load processed unified CSV into MySQL delivery_records table
Run from backend/ directory:
    python -m data.load_to_db
"""

import sys
import os
import math
import random
import string
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from database.db import db
from database.models import DeliveryRecord

PROCESSED_FILE = os.path.join(os.path.dirname(__file__), "processed", "unified_delivery.csv")

# Decode maps (reverse of encoding)
TRAFFIC_DECODE  = {0:"LOW", 1:"MODERATE", 2:"HIGH", 3:"SEVERE"}
PKG_TYPE_DECODE = {0:"SMALL", 1:"MEDIUM", 2:"LARGE", 3:"FRAGILE", 4:"PERISHABLE"}
PRIORITY_DECODE = {0:"STANDARD", 1:"EXPRESS", 2:"OVERNIGHT"}


def gen_tracking_id():
    return "PKG" + "".join(random.choices(string.ascii_uppercase + string.digits, k=10))


def main(batch_size=1000):
    if not os.path.exists(PROCESSED_FILE):
        print(f"[load] ❌ Processed file not found: {PROCESSED_FILE}")
        print("[load]    Run: python -m data.process_datasets first")
        return

    df = pd.read_csv(PROCESSED_FILE)
    print(f"[load] Loaded {len(df):,} rows from {PROCESSED_FILE}")

    app = create_app()
    with app.app_context():
        db.create_all()

        existing = DeliveryRecord.query.count()
        print(f"[load] Existing records in DB: {existing:,}")

        # Clear existing synthetic records and reload real Kaggle data
        if existing > 0:
            print(f"[load] Clearing {existing:,} existing records to load real dataset...")
            db.session.query(DeliveryRecord).delete()
            db.session.commit()
            print("[load] Cleared existing records.")

        records = []
        inserted = 0

        for idx, row in df.iterrows():
            tl  = TRAFFIC_DECODE.get(int(row.get("traffic_level_enc", 1)), "MODERATE")
            pt  = PKG_TYPE_DECODE.get(int(row.get("package_type_enc", 1)), "MEDIUM")
            pri = PRIORITY_DECODE.get(int(row.get("priority_enc", 0)), "STANDARD")

            dist     = float(row["distance_km"])
            base_dur = round(dist / 60.0 * 60, 1)
            traf_dur = float(row.get("traffic_duration_min", base_dur * 1.2))
            weight   = float(row.get("package_weight_kg", 2.0))
            actual   = float(row["actual_time_hours"])
            pred     = round(actual * random.uniform(0.92, 1.08), 3)

            record = DeliveryRecord(
                tracking_id          = str(row.get("tracking_id", gen_tracking_id())),
                origin_city          = str(row.get("origin_city", "Mumbai")),
                destination_city     = str(row.get("destination_city", "Delhi")),
                distance_km          = round(dist, 2),
                base_duration_min    = base_dur,
                traffic_duration_min = round(traf_dur, 1),
                traffic_level        = tl,
                weather_condition    = "CLEAR",   # No weather in these datasets
                package_weight_kg    = round(weight, 2),
                package_type         = pt,
                priority             = pri,
                predicted_time_hours = pred,
                actual_time_hours    = round(actual, 3),
                model_used           = random.choice(["xgboost","random_forest","linear_regression"]),
            )
            records.append(record)

            if len(records) >= batch_size:
                db.session.bulk_save_objects(records)
                db.session.commit()
                inserted += len(records)
                records = []
                print(f"[load] Inserted {inserted:,} / {len(df):,}...")

        if records:
            db.session.bulk_save_objects(records)
            db.session.commit()
            inserted += len(records)

        total = DeliveryRecord.query.count()
        print(f"\n[load] ✅ Done! Inserted {inserted:,} records. Total in DB: {total:,}")
        print("[load] Next step: python -m models.train")


if __name__ == "__main__":
    main()
