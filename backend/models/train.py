"""
models/train.py — Train ML models for Delivery Time Prediction
Supports 14 ML models: Baseline, Tree-Based, Boosting, Distance-Based, Ensemble

Data sources (priority order):
  1. data/processed/unified_delivery.csv  (real Kaggle datasets, preferred)
  2. MySQL delivery_records table          (fallback / synthetic)

Run from backend/ directory:
    python -m models.train
"""

import sys
import os
import json
import time
import joblib
import warnings
import numpy as np
import pandas as pd
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ── Suppress All Warnings & Windows loky Subprocess Tracebacks ──────
os.environ["LOKY_MAX_CPU_COUNT"] = str(os.cpu_count() or 4)
os.environ["PYTHONWARNINGS"] = "ignore"
warnings.filterwarnings("ignore")
try:
    import joblib.externals.loky.backend.context as _loky_ctx
    _loky_ctx.physical_cores_cache = os.cpu_count() or 4
except Exception:
    pass

from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import (
    RandomForestRegressor, ExtraTreesRegressor,
    GradientBoostingRegressor, StackingRegressor
)
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from xgboost import XGBRegressor

# Optional boosting imports
_HAS_LIGHTGBM = False
_HAS_CATBOOST = False

try:
    from lightgbm import LGBMRegressor
    _HAS_LIGHTGBM = True
except ImportError:
    pass

try:
    from catboost import CatBoostRegressor
    _HAS_CATBOOST = True
except ImportError:
    pass

# Deep Learning TabNet import
_HAS_TABNET = False
try:
    from models.tabnet_model import TabNetEstimator
    _HAS_TABNET = True
except ImportError:
    try:
        from tabnet_model import TabNetEstimator
        _HAS_TABNET = True
    except ImportError:
        pass

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
def evaluate(model, X_test, y_test, name, needs_scaling=False, scaler=None):
    X_eval = scaler.transform(X_test) if needs_scaling and scaler else X_test
    preds = model.predict(X_eval)
    rmse  = float(np.sqrt(mean_squared_error(y_test, preds)))
    mae   = float(mean_absolute_error(y_test, preds))
    r2    = float(r2_score(y_test, preds))
    tol_15m = round(float(np.mean(np.abs(preds - y_test) <= 0.25) * 100), 2)
    tol_30m = round(float(np.mean(np.abs(preds - y_test) <= 0.50) * 100), 2)
    tol_60m = round(float(np.mean(np.abs(preds - y_test) <= 1.00) * 100), 2)
    mape    = round(float(np.mean(np.abs((y_test - preds) / np.clip(y_test, 0.1, None))) * 100), 2)
    print(f"  [{name:25s}] RMSE={rmse:.4f}h  MAE={mae:.4f}h  R²={r2:.4f}  Tol±30m={tol_30m}%  MAPE={mape}%")
    return {
        "rmse": rmse, "mae": mae, "r2": r2, "mape": mape,
        "tolerance_15m": tol_15m, "tolerance_30m": tol_30m,
        "tolerance_60m": tol_60m, "accuracy_score": tol_30m,
    }


# ── Model Definitions ───────────────────────────────────────────
def detect_gpu_acceleration():
    gpu = {"available": False, "name": "CPU", "xgb_device": "cpu", "cb_task_type": "CPU"}
    try:
        import subprocess
        res = subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                             capture_output=True, text=True, timeout=4)
        if res.returncode == 0 and res.stdout.strip():
            gpu["available"] = True
            gpu["name"] = res.stdout.strip()
            import xgboost as xgb
            try:
                test_xgb = xgb.XGBRegressor(device="cuda", tree_method="hist", n_estimators=1)
                test_xgb.fit(np.zeros((4, 2)), np.zeros(4))
                gpu["xgb_device"] = "cuda"
            except Exception:
                pass
            import catboost
            try:
                test_cb = catboost.CatBoostRegressor(iterations=1, task_type="GPU", verbose=0)
                test_cb.fit(np.random.randn(10, 2), np.random.randn(10))
                gpu["cb_task_type"] = "GPU"
            except Exception:
                pass
    except Exception:
        pass
    return gpu


def get_model_configs():
    """Return all model configurations."""
    configs = []
    gpu = detect_gpu_acceleration()
    if gpu["available"]:
        print(f"[train] ⚡ GPU Acceleration Detected: {gpu['name']}")
        print(f"        • XGBoost:  {gpu['xgb_device'].upper()} (tree_method='hist')")
        print(f"        • CatBoost: {gpu['cb_task_type']} (task_type='{gpu['cb_task_type']}')")

    # ── Baseline ─────────────────────────────────────────────────
    configs.append(("linear_regression", "Linear Regression", True,
                    LinearRegression()))
    configs.append(("ridge", "Ridge Regression", True,
                    Ridge(alpha=1.0, random_state=42)))
    configs.append(("lasso", "Lasso Regression", True,
                    Lasso(alpha=0.01, random_state=42, max_iter=5000)))
    configs.append(("elastic_net", "Elastic Net", True,
                    ElasticNet(alpha=0.01, l1_ratio=0.5, random_state=42, max_iter=5000)))

    # ── Tree-Based (Maximized Capacity: 1000 Trees) ─────────────
    configs.append(("decision_tree", "Decision Tree", False,
                    DecisionTreeRegressor(max_depth=16, min_samples_split=6,
                                         min_samples_leaf=2, random_state=42)))
    configs.append(("random_forest", "Random Forest", False,
                    RandomForestRegressor(n_estimators=1000, max_depth=18,
                                         min_samples_split=4, min_samples_leaf=2,
                                         max_features="sqrt", random_state=42, n_jobs=-1)))
    configs.append(("extra_trees", "Extra Trees", False,
                    ExtraTreesRegressor(n_estimators=1000, max_depth=18,
                                       min_samples_split=4, min_samples_leaf=2,
                                       random_state=42, n_jobs=-1)))

    # ── Boosting (Maximized Capacity: 1000 Iterations / GPU Acceleration) ───────────
    configs.append(("gradient_boosting", "Gradient Boosting", False,
                    GradientBoostingRegressor(n_estimators=500, max_depth=6,
                                             learning_rate=0.04, subsample=0.85,
                                             min_samples_split=4, min_samples_leaf=2,
                                             random_state=42)))
    configs.append(("xgboost", "XGBoost", False,
                    XGBRegressor(n_estimators=1000, max_depth=8,
                                 learning_rate=0.03, subsample=0.85,
                                 colsample_bytree=0.85, min_child_weight=3,
                                 reg_alpha=0.1, reg_lambda=1.0,
                                 tree_method="hist", device=gpu["xgb_device"],
                                 random_state=42, n_jobs=-1, verbosity=0)))

    if _HAS_LIGHTGBM:
        configs.append(("lightgbm", "LightGBM", False,
                        LGBMRegressor(n_estimators=1000, max_depth=9, num_leaves=63,
                                      learning_rate=0.03, subsample=0.85,
                                      colsample_bytree=0.85, min_child_weight=3,
                                      reg_alpha=0.1, reg_lambda=1.0,
                                      random_state=42, n_jobs=-1, verbose=-1)))

    if _HAS_CATBOOST:
        configs.append(("catboost", "CatBoost", False,
                        CatBoostRegressor(iterations=1000, depth=8,
                                          learning_rate=0.03, l2_leaf_reg=2.0,
                                          task_type=gpu["cb_task_type"],
                                          random_seed=42, verbose=0,
                                          loss_function="RMSE")))

    # ── Distance-Based ───────────────────────────────────────────
    configs.append(("knn", "K-Nearest Neighbors", True,
                    KNeighborsRegressor(n_neighbors=9, weights="distance",
                                       algorithm="auto", n_jobs=-1)))
    configs.append(("svr", "Support Vector Regressor", True,
                    SVR(kernel="rbf", C=25.0, epsilon=0.05, gamma="scale")))

    # ── Deep Learning for Tabular Data ───────────────────────────
    configs.append(("mlp", "Multi-Layer Perceptron (MLP)", True,
                    MLPRegressor(hidden_layer_sizes=(512, 256, 128, 64),
                                 activation="relu", solver="adam", alpha=0.0001,
                                 batch_size=512, learning_rate="adaptive",
                                 max_iter=200, early_stopping=True, random_state=42)))

    if _HAS_TABNET:
        configs.append(("tabnet", "TabNet Regressor", True,
                        TabNetEstimator(n_d=24, n_a=24, n_steps=5, gamma=1.3,
                                        max_epochs=25, batch_size=1024, seed=42)))

    return configs


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

    # Scaler for models that need it
    scaler         = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled  = scaler.transform(X_test)

    metrics = {}
    trained_models = {}
    importances = {}

    model_configs = get_model_configs()
    total = len(model_configs)

    for idx, (key, name, needs_scaling, estimator) in enumerate(model_configs, 1):
        print(f"[train] [{idx}/{total}] Training {name}...")

        t_start = time.time()
        try:
            X_tr = X_train_scaled if needs_scaling else X_train

            # Special handling
            if key == "xgboost":
                estimator.fit(X_tr, y_train,
                              eval_set=[(X_test_scaled if needs_scaling else X_test, y_test)],
                              verbose=False)
            elif key == "svr":
                # SVR is slow — subsample for speed
                n_svr = min(len(X_tr), 15000)
                if n_svr < len(X_tr):
                    print(f"  [svr] Subsampling to {n_svr:,} for speed")
                    idx_sub = np.random.choice(len(X_tr), n_svr, replace=False)
                    estimator.fit(X_tr[idx_sub], y_train[idx_sub])
                else:
                    estimator.fit(X_tr, y_train)
            else:
                estimator.fit(X_tr, y_train)

            t_train = time.time() - t_start

            metrics[key] = evaluate(estimator, X_test, y_test, name,
                                    needs_scaling=needs_scaling, scaler=scaler)
            metrics[key]["training_time_seconds"] = round(t_train, 2)

            # Save model
            joblib.dump(estimator, os.path.join(SAVED_DIR, f"{key}.pkl"))
            trained_models[key] = estimator

            # Feature importance for tree/boosting models
            if hasattr(estimator, "feature_importances_"):
                importances[key] = dict(zip(FEATURE_COLUMNS,
                                            estimator.feature_importances_.tolist()))

            print(f"  [{name:25s}] Trained in {t_train:.1f}s\n")

        except Exception as e:
            print(f"  [{name:25s}] FAILED: {e}\n")

    # ── Stacking Regressor ───────────────────────────────────────
    if len(trained_models) >= 3:
        print(f"[train] [{total+1}/{total+1}] Training Stacking Regressor...")
        t_start = time.time()
        try:
            # Pick top 3 models by R² for stacking (CatBoost, LightGBM, XGBoost, Random Forest)
            top3_keys = sorted(
                [k for k in metrics if k not in ("linear_regression", "ridge", "lasso",
                                                  "elastic_net", "knn", "svr", "decision_tree", "tabnet", "mlp")],
                key=lambda k: metrics[k]["r2"], reverse=True
            )[:3]

            if len(top3_keys) < 2:
                top3_keys = sorted(metrics.keys(), key=lambda k: metrics[k]["r2"], reverse=True)[:3]

            base_estimators = []
            for k in top3_keys:
                # Reload fresh estimator for stacking (sklearn needs unfitted)
                for cfg_key, cfg_name, cfg_scale, cfg_est in model_configs:
                    if cfg_key == k:
                        import copy
                        base_estimators.append((k, copy.deepcopy(cfg_est)))
                        break

            if len(base_estimators) >= 2:
                stacking = StackingRegressor(
                    estimators=base_estimators,
                    final_estimator=Ridge(alpha=1.0),
                    cv=3, n_jobs=-1
                )
                stacking.fit(X_train, y_train)
                t_train = time.time() - t_start

                metrics["stacking"] = evaluate(stacking, X_test, y_test,
                                               "Stacking Regressor")
                metrics["stacking"]["training_time_seconds"] = round(t_train, 2)
                metrics["stacking"]["base_models"] = top3_keys

                joblib.dump(stacking, os.path.join(SAVED_DIR, "stacking.pkl"))
                print(f"  [Stacking Regressor       ] Trained in {t_train:.1f}s  (base: {top3_keys})\n")
        except Exception as e:
            print(f"  [Stacking Regressor       ] FAILED: {e}\n")

    # Save scaler
    joblib.dump(scaler, os.path.join(SAVED_DIR, "scaler.pkl"))

    # ── Best model ───────────────────────────────────────────────
    best = min(metrics, key=lambda k: metrics[k]["rmse"])
    print(f"\n[train] 🏆 Best model: {best} (RMSE={metrics[best]['rmse']:.4f}h, R²={metrics[best]['r2']:.4f})")

    # ── Leaderboard ──────────────────────────────────────────────
    print(f"\n{'─' * 90}")
    print(f"  {'Rank':>4}  {'Model':30s}  {'R²':>10}  {'RMSE(h)':>9}  {'MAE(h)':>8}  {'MAPE%':>7}  {'±30m%':>7}")
    print(f"{'─' * 90}")
    sorted_models = sorted(metrics.items(), key=lambda x: x[1]["r2"], reverse=True)
    for rank, (key, met) in enumerate(sorted_models, 1):
        marker = " ⭐ BEST" if key == best else ""
        print(f"  {rank:4d}  {key:30s}  {met['r2']:10.6f}  {met['rmse']:9.4f}  "
              f"{met['mae']:8.4f}  {met['mape']:6.1f}%  {met['tolerance_30m']:6.1f}%{marker}")
    print(f"{'─' * 90}")

    # ── Save summary JSON ────────────────────────────────────────
    # Use XGBoost importances as default (most reliable for display)
    default_importances = importances.get("xgboost", importances.get("random_forest", {}))

    summary = {
        "trained_at":       datetime.now(timezone.utc).isoformat(),
        "training_samples": len(X_train),
        "test_samples":     len(X_test),
        "data_source":      "unified_csv" if os.path.exists(CSV_DATA) else "mysql_db",
        "best_model":       best,
        "feature_columns":  FEATURE_COLUMNS,
        "metrics":          metrics,
        "feature_importances": default_importances,
        "models_trained":   list(metrics.keys()),
        "leaderboard": [
            {"rank": i+1, "model": k, "r2": v["r2"], "rmse": v["rmse"]}
            for i, (k, v) in enumerate(sorted_models)
        ],
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

    print(f"\n[train] ✅ {len(metrics)} models saved to models/saved/")
    print("[train]    metrics.json written")
    return summary


if __name__ == "__main__":
    train()
