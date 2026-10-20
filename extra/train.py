"""
train.py — Master Unified Pipeline & Model Trainer
AI-Based Package Delivery Time Prediction System (DeliverAI)

Combines:
  1. Automated Data Cleaning & Merging (184,000+ Indian Logistics Records)
  2. 16 Machine Learning & Deep Learning Models Training with Live Progress Bars
  3. Stacking Ensemble Meta-Model
  4. Database Synchronization (SQLite / MySQL)
  5. Executive Leaderboard & Metrics Serialization

Usage:
    python train.py                  # Full automated end-to-end (clean, merge, train all)
    python train.py --skip-clean     # Train on existing processed unified_delivery.csv
    python train.py --interactive    # Launch interactive menu for individual model training
"""

import os
import sys

# ── Auto-forward to project venv if invoked from system Python ───
_venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "Scripts", "python.exe")
if os.path.exists(_venv_python) and os.path.abspath(sys.executable).lower() != os.path.abspath(_venv_python).lower():
    import subprocess
    _res = subprocess.run([_venv_python] + sys.argv)
    sys.exit(_res.returncode)

import time
import json
import random
import warnings
import argparse
from datetime import datetime, timezone

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── Suppress All Warnings & Windows loky Subprocess Tracebacks ──────
os.environ["LOKY_MAX_CPU_COUNT"] = str(os.cpu_count() or 4)
os.environ["PYTHONWARNINGS"] = "ignore"
warnings.filterwarnings("ignore")
try:
    import joblib.externals.loky.backend.context as _loky_ctx
    _loky_ctx.physical_cores_cache = os.cpu_count() or 4
except Exception:
    pass

# ── Path Setup ───────────────────────────────────────────────────
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

os.environ["PYTHONPATH"] = BACKEND_DIR

CSV_DATA  = os.path.join(BACKEND_DIR, "data", "processed", "unified_delivery.csv")
SAVED_DIR = os.path.join(BACKEND_DIR, "models", "saved")
os.makedirs(SAVED_DIR, exist_ok=True)


# ── Terminal Styling ─────────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    CYAN    = "\033[36m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    RED     = "\033[31m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    WHITE   = "\033[37m"


def banner():
    print(f"\n{C.CYAN}{'═' * 80}{C.RESET}")
    print(f"{C.BOLD}{C.WHITE}  DELIVERAI — MASTER INLAND INDIA LOGISTICS & AI TRAINING PIPELINE{C.RESET}")
    print(f"{C.DIM}  184k+ Shipments · 16 ML & Deep Learning Models · Stacking Meta-Ensemble{C.RESET}")
    print(f"{C.CYAN}{'═' * 80}{C.RESET}\n")


def step_header(step_num, total_steps, title):
    print(f"\n{C.BOLD}{C.CYAN}▶ STEP [{step_num}/{total_steps}]: {C.WHITE}{title.upper()}{C.RESET}")
    print(f"{C.DIM}{'─' * 80}{C.RESET}")


def progress_bar(current, total, width=26, label="", color=C.GREEN, start_time=None):
    filled = int(width * current / max(total, 1))
    bar = f"{'█' * filled}{'░' * (width - filled)}"
    pct = (current / max(total, 1)) * 100

    time_str = ""
    if start_time is not None and current > 0:
        elapsed = time.time() - start_time
        rate = elapsed / current
        remaining = rate * (total - current)
        m_el, s_el = divmod(int(elapsed), 60)
        m_rem, s_rem = divmod(int(remaining), 60)
        time_str = f" {C.CYAN}[Elapsed: {m_el:02d}:{s_el:02d} | ETA: {m_rem:02d}:{s_rem:02d}]{C.RESET}"

    sys.stdout.write(f"\r  {color}[{bar}]{C.RESET} {pct:5.1f}%  {label}{time_str}   ")
    if current >= total:
        sys.stdout.write("\n")
    sys.stdout.flush()


# ── Step 1: Auto-Clean & Merge Datasets ───────────────────────────
def step_clean_and_merge():
    step_header(1, 4, "Auto-Cleaning & Merging All Inland India Datasets")

    from data.process_datasets import main as process_all_datasets
    t_start = time.time()
    unified_df = process_all_datasets()

    if unified_df is None or unified_df.empty:
        print(f"\n{C.RED}❌ Error: Dataset processing failed or returned empty dataframe.{C.RESET}")
        sys.exit(1)

    elapsed = time.time() - t_start
    print(f"\n  {C.GREEN}✓ Cleaned and unified {len(unified_df):,} records in {elapsed:.1f}s{C.RESET}")
    print(f"    File: {C.DIM}{CSV_DATA}{C.RESET}")
    print(f"    Sources breakdown:")
    for src, count in unified_df["source"].value_counts().items():
        pct = (count / len(unified_df)) * 100
        print(f"      • {src:28s}: {count:7,d} shipments ({pct:4.1f}%)")

    return unified_df


# ── GPU Hardware Detection ─────────────────────────────────────────
def detect_gpu_acceleration():
    """Detect NVIDIA GPU and verify library acceleration compatibility."""
    gpu = {
        "available": False,
        "name": "CPU",
        "xgb_device": "cpu",
        "cb_task_type": "CPU",
    }
    try:
        import subprocess
        res = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=4
        )
        if res.returncode == 0 and res.stdout.strip():
            gpu["available"] = True
            gpu["name"] = res.stdout.strip()

            # Test XGBoost CUDA
            try:
                import xgboost as xgb
                test_xgb = xgb.XGBRegressor(device="cuda", tree_method="hist", n_estimators=1)
                test_xgb.fit(np.zeros((4, 2)), np.zeros(4))
                gpu["xgb_device"] = "cuda"
            except Exception:
                gpu["xgb_device"] = "cpu"

            # Test CatBoost GPU
            try:
                import catboost
                test_cb = catboost.CatBoostRegressor(iterations=1, task_type="GPU", verbose=0)
                test_cb.fit(np.random.randn(10, 2), np.random.randn(10))
                gpu["cb_task_type"] = "GPU"
            except Exception:
                gpu["cb_task_type"] = "CPU"
    except Exception:
        pass
    return gpu


# ── Step 2: Model Configuration & Training ───────────────────────
def get_model_definitions():
    from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.ensemble import (
        RandomForestRegressor, ExtraTreesRegressor, GradientBoostingRegressor,
        HistGradientBoostingRegressor, BaggingRegressor
    )
    from sklearn.neighbors import KNeighborsRegressor
    from sklearn.svm import SVR
    from sklearn.neural_network import MLPRegressor
    from xgboost import XGBRegressor
    from lightgbm import LGBMRegressor
    from catboost import CatBoostRegressor
    from models.tabnet_model import TabNetEstimator

    gpu = detect_gpu_acceleration()
    if gpu["available"]:
        print(f"  {C.GREEN}⚡ GPU Acceleration Detected: {C.BOLD}{gpu['name']}{C.RESET}")
        print(f"    • XGBoost:  {C.CYAN}{gpu['xgb_device'].upper()}{C.RESET} (tree_method='hist')")
        print(f"    • CatBoost: {C.CYAN}{gpu['cb_task_type']}{C.RESET} (task_type='{gpu['cb_task_type']}')")
        print(f"    • LightGBM / Sklearn: Multi-core CPU (n_jobs=-1)\n")
    else:
        print(f"  {C.DIM}• Running on multi-core CPU (n_jobs=-1 enabled){C.RESET}\n")

    models = [
        # Baseline
        ("linear_regression", "Linear Regression", True, LinearRegression()),
        ("ridge", "Ridge Regression", True, Ridge(alpha=1.0, random_state=42)),
        ("lasso", "Lasso Regression", True, Lasso(alpha=0.01, random_state=42, max_iter=3000)),
        ("elastic_net", "Elastic Net", True, ElasticNet(alpha=0.01, l1_ratio=0.5, random_state=42, max_iter=3000)),

        # Tree-Based (Maximized Capacity: 1000 Trees / Deep Branches)
        ("decision_tree", "Decision Tree", False,
         DecisionTreeRegressor(max_depth=16, min_samples_split=6, min_samples_leaf=2, random_state=42)),
        ("random_forest", "Random Forest", False,
         RandomForestRegressor(n_estimators=1000, max_depth=18, min_samples_split=4, min_samples_leaf=2,
                               max_features="sqrt", random_state=42, n_jobs=-1)),
        ("extra_trees", "Extra Trees Regressor", False,
         ExtraTreesRegressor(n_estimators=1000, max_depth=18, min_samples_split=4, min_samples_leaf=2,
                            random_state=42, n_jobs=-1)),
        ("bagging", "Bagging Regressor", False,
         BaggingRegressor(estimator=DecisionTreeRegressor(max_depth=14, min_samples_split=6),
                          n_estimators=100, max_samples=0.9, random_state=42, n_jobs=-1)),

        # Boosting (Maximized Capacity: 1000 Iterations / GPU Acceleration)
        ("gradient_boosting", "Gradient Boosting", False,
         GradientBoostingRegressor(n_estimators=500, max_depth=6, learning_rate=0.04, subsample=0.85, random_state=42)),
        ("hist_gradient_boosting", "Histogram Gradient Boosting", False,
         HistGradientBoostingRegressor(max_iter=1000, max_depth=8, learning_rate=0.03, random_state=42)),
        ("xgboost", "XGBoost Regressor", False,
         XGBRegressor(n_estimators=1000, max_depth=8, learning_rate=0.03, subsample=0.85,
                      colsample_bytree=0.85, min_child_weight=3, reg_alpha=0.1, reg_lambda=1.0,
                      tree_method="hist", device=gpu["xgb_device"],
                      random_state=42, n_jobs=-1, verbosity=0)),
        ("lightgbm", "LightGBM Regressor", False,
         LGBMRegressor(n_estimators=1000, max_depth=9, num_leaves=63, learning_rate=0.03, subsample=0.85,
                       colsample_bytree=0.85, min_child_weight=3, reg_alpha=0.1, reg_lambda=1.0,
                       random_state=42, n_jobs=-1, verbose=-1)),
        ("catboost", "CatBoost Regressor", False,
         CatBoostRegressor(iterations=1000, depth=8, learning_rate=0.03, l2_leaf_reg=2.0,
                           task_type=gpu["cb_task_type"],
                           random_seed=42, verbose=0, loss_function="RMSE")),

        # Distance-Based
        ("knn", "K-Nearest Neighbors (KNN)", True,
         KNeighborsRegressor(n_neighbors=9, weights="distance", algorithm="auto", n_jobs=-1)),
        ("svr", "Support Vector Regressor (SVR)", True,
         SVR(kernel="rbf", C=25.0, epsilon=0.05, gamma="scale")),

        # Deep Learning (Tabular - Maximized Capacity)
        ("mlp", "Multi-Layer Perceptron (MLP)", True,
         MLPRegressor(hidden_layer_sizes=(512, 256, 128, 64), activation="relu", solver="adam", alpha=0.0001,
                      batch_size=512, learning_rate="adaptive", max_iter=200, early_stopping=True, random_state=42)),
        ("tabnet", "TabNet Regressor", True,
         TabNetEstimator(n_d=24, n_a=24, n_steps=5, gamma=1.3, max_epochs=25, batch_size=1024, device_name="auto", seed=42)),
    ]

    return models


def evaluate_predictions(preds, y_test):
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
    mae  = float(mean_absolute_error(y_test, preds))
    r2   = float(r2_score(y_test, preds))
    tol_15m = round(float(np.mean(np.abs(preds - y_test) <= 0.25) * 100), 2)
    tol_30m = round(float(np.mean(np.abs(preds - y_test) <= 0.50) * 100), 2)
    tol_60m = round(float(np.mean(np.abs(preds - y_test) <= 1.00) * 100), 2)
    mape    = round(float(np.mean(np.abs((y_test - preds) / np.clip(y_test, 0.1, None))) * 100), 2)

    return {
        "rmse": rmse, "mae": mae, "r2": r2, "mape": mape,
        "tolerance_15m": tol_15m, "tolerance_30m": tol_30m,
        "tolerance_60m": tol_60m, "accuracy_score": tol_30m,
    }


def step_train_models(df, filter_keys=None):
    model_count_str = "16 Machine Learning & Deep Learning Models" if not filter_keys else f"{len(filter_keys)} Selected Models"
    step_header(2, 4, f"Training {model_count_str}")

    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import StackingRegressor
    from sklearn.linear_model import Ridge
    import joblib

    from utils.feature_engineering import dataframe_features, FEATURE_COLUMNS

    X = dataframe_features(df).values.astype(np.float64)
    y = df["actual_time_hours"].values.astype(np.float64)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    print(f"  Training samples: {C.BOLD}{len(X_train):,}{C.RESET} | Holdout test samples: {C.BOLD}{len(X_test):,}{C.RESET}")
    print(f"  Features ({len(FEATURE_COLUMNS)}): {FEATURE_COLUMNS}\n")

    # Scaler for distance & neural models
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled  = scaler.transform(X_test)

    joblib.dump(scaler, os.path.join(SAVED_DIR, "scaler.pkl"))

    all_defs = get_model_definitions()
    model_defs = [m for m in all_defs if m[0] in filter_keys] if filter_keys else all_defs
    include_ensembles = (filter_keys is None or len(model_defs) >= 3)
    total_models = len(model_defs) + (2 if include_ensembles else 0)

    metrics = {}
    trained_models = {}
    importances = {}
    t_pipeline_start = time.time()

    for idx, (key, name, needs_scaling, estimator) in enumerate(model_defs, 1):
        progress_bar(idx - 1, total_models, label=f"[{idx}/{total_models}] Training {name}...", start_time=t_pipeline_start)
        t_start = time.time()
        X_tr = X_train_scaled if needs_scaling else X_train
        X_te = X_test_scaled if needs_scaling else X_test

        try:
            if key == "svr":
                n_svr = min(len(X_tr), 15000)
                idx_sub = np.random.choice(len(X_tr), n_svr, replace=False)
                estimator.fit(X_tr[idx_sub], y_train[idx_sub])
            else:
                estimator.fit(X_tr, y_train)

            preds = estimator.predict(X_te)
            t_train = time.time() - t_start

            m = evaluate_predictions(preds, y_test)
            m["training_time_seconds"] = round(t_train, 2)
            metrics[key] = m

            # Save model
            joblib.dump(estimator, os.path.join(SAVED_DIR, f"{key}.pkl"))
            trained_models[key] = estimator

            if hasattr(estimator, "feature_importances_"):
                importances[key] = dict(zip(FEATURE_COLUMNS, estimator.feature_importances_.tolist()))

        except Exception as e:
            print(f"\n  {C.RED}❌ Error training {name}: {e}{C.RESET}")

    if include_ensembles:
        # ── Train Voting Regressor ───────────────────────────────────
        progress_bar(total_models - 2, total_models, label=f"[{total_models-1}/{total_models}] Training Voting Regressor...", start_time=t_pipeline_start)
        t_start = time.time()
        try:
            candidates = ["catboost", "lightgbm", "xgboost", "random_forest", "extra_trees"]
            top_voting_keys = [k for k in candidates if k in metrics][:4]
            voting_estimators = []
            for k in top_voting_keys:
                for cfg_key, cfg_name, cfg_scale, cfg_est in model_defs:
                    if cfg_key == k:
                        import copy
                        voting_estimators.append((k, copy.deepcopy(cfg_est)))
                        break

            if len(voting_estimators) >= 2:
                from sklearn.ensemble import VotingRegressor
                voting = VotingRegressor(estimators=voting_estimators, n_jobs=-1)
                voting.fit(X_train, y_train)
                t_train = time.time() - t_start
                preds = voting.predict(X_test)

                m = evaluate_predictions(preds, y_test)
                m["training_time_seconds"] = round(t_train, 2)
                m["base_models"] = top_voting_keys
                metrics["voting"] = m
                trained_models["voting"] = voting

                joblib.dump(voting, os.path.join(SAVED_DIR, "voting.pkl"))
        except Exception as e:
            print(f"\n  {C.YELLOW}⚠️  Voting regressor warning: {e}{C.RESET}")

        # ── Train Stacking Ensemble ──────────────────────────────────
        progress_bar(total_models - 1, total_models, label=f"[{total_models}/{total_models}] Training Stacking Regressor...", start_time=t_pipeline_start)
        t_start = time.time()
        try:
            candidates = ["catboost", "lightgbm", "gradient_boosting", "extra_trees", "random_forest", "xgboost"]
            top_keys = [k for k in candidates if k in metrics][:3]

            base_estimators = []
            for k in top_keys:
                for cfg_key, cfg_name, cfg_scale, cfg_est in model_defs:
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
                preds = stacking.predict(X_test)

                m = evaluate_predictions(preds, y_test)
                m["training_time_seconds"] = round(t_train, 2)
                m["base_models"] = top_keys
                metrics["stacking"] = m
                trained_models["stacking"] = stacking

                joblib.dump(stacking, os.path.join(SAVED_DIR, "stacking.pkl"))
        except Exception as e:
            print(f"\n  {C.YELLOW}⚠️  Stacking regressor warning: {e}{C.RESET}")

    progress_bar(total_models, total_models, label=f"All {len(metrics)} models successfully trained!   ", start_time=t_pipeline_start)

    # Save metrics.json
    best_model = min(metrics, key=lambda k: metrics[k]["rmse"])
    default_imp = importances.get("xgboost", importances.get("random_forest", {}))

    sorted_models = sorted(metrics.items(), key=lambda x: x[1]["r2"], reverse=True)
    summary = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "data_source": "unified_csv",
        "best_model": best_model,
        "feature_columns": FEATURE_COLUMNS,
        "metrics": metrics,
        "feature_importances": default_imp,
        "models_trained": list(metrics.keys()),
        "leaderboard": [
            {"rank": i + 1, "model": k, "r2": v["r2"], "rmse": v["rmse"], "mae": v["mae"]}
            for i, (k, v) in enumerate(sorted_models)
        ],
    }

    with open(os.path.join(SAVED_DIR, "metrics.json"), "w") as f:
        json.dump(summary, f, indent=2)

    return summary, sorted_models, len(X_train)


# ── Step 3: Database Synchronization ─────────────────────────────
def step_sync_database(summary, sample_count):
    step_header(3, 4, "Syncing Records & Metrics to Database")

    try:
        from app import create_app
        from database.db import db
        from database.models import ModelMetric
        app = create_app()

        with app.app_context():
            db.session.query(ModelMetric).update({"is_current": False})
            db.session.commit()

            for model_name, m in summary.get("metrics", {}).items():
                db.session.add(ModelMetric(
                    model_name=model_name,
                    rmse=m["rmse"],
                    mae=m["mae"],
                    r2=m["r2"],
                    trained_on=sample_count,
                    is_current=True,
                ))
            db.session.commit()
            print(f"  {C.GREEN}✓ Synchronized {len(summary.get('metrics', {}))} model metrics with active database{C.RESET}")
    except Exception as e:
        print(f"  {C.YELLOW}ℹ️  Database sync note (using local cache): {e}{C.RESET}")


# ── Step 4: Executive Performance Report ─────────────────────────
def step_print_report(summary, sorted_models):
    step_header(4, 4, "Executive Benchmark Leaderboard")

    best_model = summary.get("best_model", "stacking")
    print(f"\n  🏆 {C.BOLD}Best Performing Model:{C.RESET} {C.GREEN}{best_model.replace('_', ' ').title()}{C.RESET}")
    print(f"  📊 {C.BOLD}Total Models Trained:{C.RESET}  {len(sorted_models)}\n")

    print(f"  {'Rank':>4}  {'Model Name':<32} | {'R² Score':<10} | {'RMSE':<9} | {'MAE':<9} | {'MAPE':<8} | {'±30m Tol':<9} | {'Time':<7}")
    print(f"  {'─' * 98}")

    for rank, (m_name, m) in enumerate(sorted_models, 1):
        disp = m_name.replace("_", " ").title()
        r2 = f"{m.get('r2', 0.0):.4f}"
        rmse = f"{m.get('rmse', 0.0):.3f}h"
        mae = f"{m.get('mae', 0.0):.3f}h"
        mape = f"{m.get('mape', 0.0):.1f}%"
        tol = f"{m.get('tolerance_30m', 0.0):.1f}%"
        t_sec = f"{m.get('training_time_seconds', 0.0):.1f}s"
        marker = f" {C.YELLOW}★ BEST{C.RESET}" if m_name == best_model else ""

        print(f"  {rank:4d}  {disp:<32} | {r2:<10} | {rmse:<9} | {mae:<9} | {mape:<8} | {tol:<9} | {t_sec:<7}{marker}")

    print(f"  {'─' * 98}")
    print(f"\n  {C.BOLD}Artifacts Saved:{C.RESET}")
    print(f"    • {len(sorted_models)} Model files: {C.DIM}{SAVED_DIR}/*.pkl{C.RESET}")
    print(f"    • Summary metrics:     {C.DIM}{SAVED_DIR}/metrics.json{C.RESET}")


# ── Interactive Mode (Self-Contained) ────────────────────────────
def run_interactive(df):
    banner()
    print(f"  {C.BOLD}DeliverAI — Interactive Model Selection Console{C.RESET}")
    print(f"  {C.DIM}Dataset: {len(df):,} records loaded from {CSV_DATA}{C.RESET}\n")
    print(f"  {C.GREEN}[1]{C.RESET}  Train All 16 Models + Stacking Ensemble (Recommended)")
    print(f"  {C.GREEN}[2]{C.RESET}  Top 5 Performers (Random Forest, CatBoost, LightGBM, XGBoost, Stacking)")
    print(f"  {C.GREEN}[3]{C.RESET}  Boosting Showdown (CatBoost, LightGBM, XGBoost, Gradient Boosting)")
    print(f"  {C.GREEN}[4]{C.RESET}  Deep Learning Models (Multi-Layer Perceptron MLP, TabNet)")
    print(f"  {C.GREEN}[5]{C.RESET}  Baseline Benchmark (Linear Regression, Ridge, Lasso, Elastic Net)")
    print(f"  {C.GREEN}[0]{C.RESET}  Exit")

    try:
        choice = input(f"\n  {C.CYAN}▶ Enter choice [1-5, or 0]: {C.RESET}").strip()
    except (KeyboardInterrupt, EOFError):
        return

    if choice == "0":
        print(f"\n  {C.DIM}Exited.{C.RESET}\n")
        return

    selected_filter = None
    if choice == "2":
        selected_filter = ["random_forest", "catboost", "lightgbm", "xgboost"]
    elif choice == "3":
        selected_filter = ["catboost", "lightgbm", "xgboost", "gradient_boosting"]
    elif choice == "4":
        selected_filter = ["mlp", "tabnet"]
    elif choice == "5":
        selected_filter = ["linear_regression", "ridge", "lasso", "elastic_net"]

    summary, sorted_models, train_count = step_train_models(df, filter_keys=selected_filter)
    step_sync_database(summary, train_count)
    step_print_report(summary, sorted_models)


# ── Main Entrypoint ──────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="DeliverAI Master Data & Training Pipeline")
    parser.add_argument("--skip-clean", action="store_true", help="Skip data processing and train on existing CSV")
    parser.add_argument("--interactive", "-i", action="store_true", help="Launch interactive model selection menu")
    args = parser.parse_args()

    # Load data
    if args.skip_clean and os.path.exists(CSV_DATA):
        banner()
        print(f"  {C.CYAN}ℹ️  Skipping data processing; using existing: {CSV_DATA}{C.RESET}")
        df = pd.read_csv(CSV_DATA)
    elif not os.path.exists(CSV_DATA):
        banner()
        df = step_clean_and_merge()
    elif not args.interactive:
        banner()
        df = step_clean_and_merge()
    else:
        df = pd.read_csv(CSV_DATA)

    if args.interactive:
        run_interactive(df)
        return

    t_start = time.time()

    # Step 2: Train all models
    summary, sorted_models, train_count = step_train_models(df)

    # Step 3: Sync to Database
    step_sync_database(summary, train_count)

    # Step 4: Executive Report
    step_print_report(summary, sorted_models)

    elapsed = time.time() - t_start
    print(f"\n{C.CYAN}{'═' * 80}{C.RESET}")
    print(f"{C.BOLD}{C.GREEN}  ✅ COMPLETE PIPELINE FINISHED IN {elapsed:.1f}s!{C.RESET}")
    print(f"  Run {C.BOLD}python main.py{C.RESET} to start the Web Command Center & Live Predictions")
    print(f"{C.CYAN}{'═' * 80}{C.RESET}\n")


if __name__ == "__main__":
    main()
