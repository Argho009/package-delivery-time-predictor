"""
models/train.py — Train XGBoost, Random Forest, and Linear Regression models
Supports two data sources (priority order):
  1. data/processed/unified_delivery.csv  (real Kaggle datasets, preferred)
  2. MySQL delivery_records table          (fallback / synthetic)

Run from backend/ directory:
    python -m models.train
"""

import sys
import os
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

from app import create_app
from database.db import db
from database.models import DeliveryRecord, ModelMetric
from utils.feature_engineering import dataframe_features, FEATURE_COLUMNS

SAVED_DIR    = os.path.join(os.path.dirname(__file__), "saved")
CSV_DATA     = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            "data", "processed", "unified_delivery.csv")
os.makedirs(SAVED_DIR, exist_ok=True)


# ── Data loaders ─────────────────────────────────────────────────
def load_from_csv() -> pd.DataFrame:
    """Load real Kaggle data from unified_delivery.csv."""
    df = pd.read_csv(CSV_DATA)
    df = df.dropna(subset=["actual_time_hours"])
    df = df[df["actual_time_hours"] > 0]
    print(f"[train] Loaded {len(df):,} rows from unified CSV")
    print(f"[train] Sources: {df['source'].value_counts().to_dict()}")
    return df


def load_from_db(app) -> pd.DataFrame:
    """Fallback: load from MySQL delivery_records."""
    with app.app_context():
        records = DeliveryRecord.query.filter(
            DeliveryRecord.actual_time_hours.isnot(None)
        ).all()

    if not records:
        raise RuntimeError("No training data found. Run data pipeline first.")

    rows = [{
        "distance_km":          r.distance_km,
        "traffic_duration_min": r.traffic_duration_min,
        "traffic_level_enc":    {"LOW":0,"MODERATE":1,"HIGH":2,"SEVERE":3}.get(r.traffic_level, 1),
        "package_weight_kg":    r.package_weight_kg,
        "package_type_enc":     {"SMALL":0,"MEDIUM":1,"LARGE":2,"FRAGILE":3,"PERISHABLE":4}.get(r.package_type, 1),
        "priority_enc":         {"STANDARD":0,"EXPRESS":1,"OVERNIGHT":2}.get(r.priority, 0),
        "shipping_mode_enc":    0,
        "actual_time_hours":    r.actual_time_hours,
        "source":               "mysql_db",
    } for r in records]

    df = pd.DataFrame(rows)
    print(f"[train] Loaded {len(df):,} rows from MySQL DB")
    return df


def load_training_data(app) -> pd.DataFrame:
    if os.path.exists(CSV_DATA):
        return load_from_csv()
    print("[train] ⚠️  unified_delivery.csv not found, falling back to DB...")
    return load_from_db(app)


# ── Evaluation ───────────────────────────────────────────────────
def evaluate(model, X_test, y_test, name):
    preds = model.predict(X_test)
    rmse  = float(np.sqrt(mean_squared_error(y_test, preds)))
    mae   = float(mean_absolute_error(y_test, preds))
    r2    = float(r2_score(y_test, preds))
    print(f"  [{name:20s}] RMSE={rmse:.4f}h  MAE={mae:.4f}h  R²={r2:.4f}")
    return {"rmse": rmse, "mae": mae, "r2": r2}


# ── Main training ─────────────────────────────────────────────────
def train():
    app = create_app()

    print("[train] Loading data...")
    df = load_training_data(app)

    X = dataframe_features(df).values.astype(np.float64)
    y = df["actual_time_hours"].values.astype(np.float64)

    print(f"[train] Features: {FEATURE_COLUMNS}")
    print(f"[train] Target stats: min={y.min():.2f}h  max={y.max():.2f}h  "
          f"mean={y.mean():.2f}h  std={y.std():.2f}h")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42)

    print(f"[train] Train: {len(X_train):,}  Test: {len(X_test):,}\n")

    # Scaler for Linear Regression
    scaler         = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled  = scaler.transform(X_test)

    metrics = {}

    # ── 1. XGBoost ──────────────────────────────────────────────
    print("[train] Training XGBoost...")
    xgb = XGBRegressor(
        n_estimators=400,
        max_depth=7,
        learning_rate=0.04,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=5,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=-1,
        verbosity=0,
    )
    xgb.fit(X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False)
    metrics["xgboost"] = evaluate(xgb, X_test, y_test, "XGBoost")
    joblib.dump(xgb, os.path.join(SAVED_DIR, "xgboost.pkl"))

    # Feature importance
    importances = dict(zip(FEATURE_COLUMNS, xgb.feature_importances_.tolist()))
    print(f"  Feature importances: { {k: round(v,3) for k,v in sorted(importances.items(), key=lambda x: -x[1])} }")

    # ── 2. Random Forest ────────────────────────────────────────
    print("\n[train] Training Random Forest...")
    rf = RandomForestRegressor(
        n_estimators=300,
        max_depth=14,
        min_samples_split=5,
        min_samples_leaf=3,
        max_features="sqrt",
        random_state=42,
        n_jobs=-1,
    )
    rf.fit(X_train, y_train)
    metrics["random_forest"] = evaluate(rf, X_test, y_test, "Random Forest")
    joblib.dump(rf, os.path.join(SAVED_DIR, "random_forest.pkl"))

    # ── 3. Linear Regression ────────────────────────────────────
    print("\n[train] Training Linear Regression...")
    lr = LinearRegression()
    lr.fit(X_train_scaled, y_train)
    metrics["linear_regression"] = evaluate(lr, X_test_scaled, y_test, "Linear Regression")
    joblib.dump(lr, os.path.join(SAVED_DIR, "linear_regression.pkl"))

    # Save scaler (needed for LR at inference)
    joblib.dump(scaler, os.path.join(SAVED_DIR, "scaler.pkl"))

    # ── Best model ───────────────────────────────────────────────
    best = min(metrics, key=lambda k: metrics[k]["rmse"])
    print(f"\n[train] 🏆 Best model: {best} (RMSE={metrics[best]['rmse']:.4f}h)")

    # ── Save summary JSON ────────────────────────────────────────
    summary = {
        "trained_at":       datetime.utcnow().isoformat(),
        "training_samples": len(X_train),
        "test_samples":     len(X_test),
        "data_source":      "unified_csv" if os.path.exists(CSV_DATA) else "mysql_db",
        "best_model":       best,
        "feature_columns":  FEATURE_COLUMNS,
        "metrics":          metrics,
        "feature_importances": importances,
    }
    with open(os.path.join(SAVED_DIR, "metrics.json"), "w") as f:
        json.dump(summary, f, indent=2)

    # ── Persist to DB ────────────────────────────────────────────
    with app.app_context():
        db.session.query(ModelMetric).update({"is_current": False})
        db.session.commit()
        for model_name, m in metrics.items():
            db.session.add(ModelMetric(
                model_name = model_name,
                rmse       = m["rmse"],
                mae        = m["mae"],
                r2         = m["r2"],
                trained_on = len(X_train),
                is_current = True,
            ))
        db.session.commit()

    print("\n[train] ✅ Models saved to models/saved/")
    print("[train]    metrics.json written")
    return summary


if __name__ == "__main__":
    train()
