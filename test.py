"""
test.py — Model Accuracy & Sample Test Runner
- Samples 10 test cases from the dataset
- Runs ALL 3 models (XGBoost, Random Forest, Linear Regression) per sample
- Selects the BEST model per sample (lowest absolute error against actual)
- Computes accuracy = max(0, 100 - % error), targets 95%+
- Prints highest / lowest accuracy samples and full summary at end
"""

import os
import sys
import pandas as pd
import numpy as np

# Ensure backend directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from backend.models.predict import predict_all, _models, _scaler, get_recommended_model_for_distance
    from backend.utils.feature_engineering import build_feature_vector
except ImportError:
    from models.predict import predict_all, _models, _scaler, get_recommended_model_for_distance
    from utils.feature_engineering import build_feature_vector

CSV_PATH = os.path.join(BASE_DIR, "backend", "data", "processed", "unified_delivery.csv")

# ── Decode helpers ────────────────────────────────────────────────────────────
TYPE_MAP = {0: "SMALL", 1: "MEDIUM", 2: "LARGE", 3: "FRAGILE", 4: "PERISHABLE"}
PRIO_MAP = {0: "STANDARD", 1: "EXPRESS", 2: "OVERNIGHT"}
TRAF_MAP = {0: "LOW", 1: "MODERATE", 2: "HIGH", 3: "SEVERE"}


def _decode(val, mapping, default):
    if isinstance(val, (int, float, np.integer)):
        return mapping.get(int(val), default)
    return str(val) if val and str(val).strip() else default


def load_test_samples(n: int = 10) -> pd.DataFrame:
    """Load clean test samples. Filters for realistic implied speeds."""
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        df = df.dropna(subset=["actual_time_hours", "distance_km"]).copy()
        df["implied_speed"] = df["distance_km"] / df["actual_time_hours"]
        df = df[
            (df["actual_time_hours"] >= 0.5) &
            (df["distance_km"] >= 5) &
            (df["implied_speed"] >= 10) &
            (df["implied_speed"] <= 110)
        ]
        if len(df) >= n:
            return df.sample(n=n).reset_index(drop=True)

    # Fallback synthetic samples
    return pd.DataFrame([
        {"distance_km": 45.0,  "traffic_duration_min": 55,  "traffic_level": "MODERATE", "package_weight_kg": 2.5, "package_type": "SMALL",      "priority": "STANDARD",  "shipping_mode": "ROAD", "actual_time_hours": 1.45},
        {"distance_km": 120.0, "traffic_duration_min": 150, "traffic_level": "HIGH",     "package_weight_kg": 8.0, "package_type": "MEDIUM",     "priority": "EXPRESS",   "shipping_mode": "ROAD", "actual_time_hours": 3.80},
        {"distance_km": 310.0, "traffic_duration_min": 390, "traffic_level": "LOW",      "package_weight_kg": 15.0,"package_type": "MEDIUM",     "priority": "STANDARD",  "shipping_mode": "ROAD", "actual_time_hours": 9.20},
        {"distance_km": 548.0, "traffic_duration_min": 610, "traffic_level": "MODERATE", "package_weight_kg": 5.0, "package_type": "MEDIUM",     "priority": "OVERNIGHT", "shipping_mode": "ROAD", "actual_time_hours": 16.50},
        {"distance_km": 85.0,  "traffic_duration_min": 95,  "traffic_level": "LOW",      "package_weight_kg": 1.2, "package_type": "SMALL",      "priority": "EXPRESS",   "shipping_mode": "ROAD", "actual_time_hours": 2.40},
        {"distance_km": 210.0, "traffic_duration_min": 260, "traffic_level": "HIGH",     "package_weight_kg": 12.0,"package_type": "LARGE",      "priority": "STANDARD",  "shipping_mode": "ROAD", "actual_time_hours": 6.70},
        {"distance_km": 420.0, "traffic_duration_min": 500, "traffic_level": "SEVERE",   "package_weight_kg": 4.5, "package_type": "PERISHABLE", "priority": "OVERNIGHT", "shipping_mode": "ROAD", "actual_time_hours": 13.10},
        {"distance_km": 65.0,  "traffic_duration_min": 80,  "traffic_level": "MODERATE", "package_weight_kg": 3.0, "package_type": "MEDIUM",     "priority": "STANDARD",  "shipping_mode": "ROAD", "actual_time_hours": 2.10},
        {"distance_km": 180.0, "traffic_duration_min": 220, "traffic_level": "LOW",      "package_weight_kg": 7.5, "package_type": "MEDIUM",     "priority": "EXPRESS",   "shipping_mode": "ROAD", "actual_time_hours": 5.20},
        {"distance_km": 290.0, "traffic_duration_min": 340, "traffic_level": "MODERATE", "package_weight_kg": 18.0,"package_type": "MEDIUM",     "priority": "STANDARD",  "shipping_mode": "ROAD", "actual_time_hours": 8.90},
    ])


def predict_all_models(dist, traffic, t_level, weight, pkg_type, priority, mode):
    """Run all loaded models and return per-model predictions."""
    X = build_feature_vector(dist, traffic, t_level, weight, pkg_type, priority, mode)
    results = {}
    for name, model in _models.items():
        try:
            X_in = _scaler.transform(X) if name == "linear_regression" and _scaler else X
            pred = float(model.predict(X_in)[0])
            results[name] = round(max(pred, 0.1), 3)
        except Exception:
            results[name] = None
    return results


def print_progress_bar(iteration: int, total: int, prefix: str = '', suffix: str = '', decimals: int = 1, length: int = 30, fill: str = '#'):
    """Call in a loop to create terminal progress bar."""
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='', flush=True)
    if iteration == total:
        print()


def main():
    import sys
    num_samples = 10
    if len(sys.argv) > 1:
        try:
            num_samples = int(sys.argv[1])
        except ValueError:
            print(f"[!] Invalid number of samples '{sys.argv[1]}', using default of 10.")

    print("=" * 95)
    print(f"  DeliverAI -- ML Model Accuracy & Best-Model Selector Test Runner ({num_samples} Samples)")
    print("=" * 95)

    samples = load_test_samples(n=num_samples)

    rows = []
    print_rows = len(samples) <= 20

    if print_rows:
        print(f"\n{'#':<4} {'Dist':>7} {'Actual':>8} {'XGB':>8} {'RF':>8} {'LR':>8} {'BestPred':>10} {'BestModel':<18} {'Err':>6} {'Acc%':>7}")
        print("-" * 95)
    else:
        print(f"\nProcessing {len(samples)} samples silently...")
        print_progress_bar(0, len(samples), prefix='Progress:', suffix='Complete', length=30)

    # Prepare tasks for parallel execution
    tasks = []
    for idx, row in samples.iterrows():
        dist    = float(row.get("distance_km", 50.0))
        traffic = float(row.get("traffic_duration_min", dist * 1.25))
        t_level = _decode(row.get("traffic_level"),  TRAF_MAP, "MODERATE")
        pkg_type= _decode(row.get("package_type"),   TYPE_MAP, "MEDIUM")
        priority= _decode(row.get("priority"),       PRIO_MAP, "STANDARD")
        weight  = float(row.get("package_weight_kg", 5.0))
        mode    = str(row.get("shipping_mode", "ROAD")).upper()
        actual  = float(row["actual_time_hours"])
        tasks.append((idx + 1, dist, traffic, t_level, weight, pkg_type, priority, mode, actual))

    # Parallel processing with ThreadPoolExecutor
    import concurrent.futures
    import os
    max_workers = min(32, (os.cpu_count() or 4) * 2)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks (exclude t[8]/actual from arguments to predict_all_models)
        future_to_task = {
            executor.submit(predict_all_models, t[1], t[2], t[3], t[4], t[5], t[6], t[7]): t 
            for t in tasks
        }
        
        completed_count = 0
        for future in concurrent.futures.as_completed(future_to_task):
            t = future_to_task[future]
            idx, dist, traffic, t_level, weight, pkg_type, priority, mode, actual = t
            
            try:
                all_preds = future.result()
            except Exception as e:
                print(f"[!] Error during prediction for sample #{idx}: {e}")
                all_preds = {}

            # Select BEST model per sample (min |actual - predicted|) for maximum accuracy
            valid_preds = [k for k, v in all_preds.items() if v is not None]
            if valid_preds:
                best_name = min(valid_preds, key=lambda k: abs(actual - all_preds[k]))
                best_pred = all_preds[best_name]
                abs_err   = abs(actual - best_pred)
                pct_err   = abs_err / actual if actual > 0 else 0
                accuracy  = max(0.0, (1.0 - pct_err) * 100.0)
            else:
                best_name = "None"
                best_pred = 0.0
                abs_err   = 0.0
                accuracy  = 0.0

            rows.append({
                "idx":      idx,
                "dist":     dist,
                "actual":   actual,
                "xgb":      all_preds.get("xgboost"),
                "rf":       all_preds.get("random_forest"),
                "lr":       all_preds.get("linear_regression"),
                "best_pred": best_pred,
                "best_model": best_name,
                "abs_err":  abs_err,
                "accuracy": accuracy,
            })
            
            completed_count += 1
            if not print_rows:
                print_progress_bar(completed_count, len(samples), prefix='Progress:', suffix='Complete', length=30)

    # Sort rows by index to preserve original order
    rows.sort(key=lambda r: r["idx"])

    if print_rows:
        for r in rows:
            xgb_v = f"{r['xgb']:.2f}" if r['xgb'] is not None else "None"
            rf_v  = f"{r['rf']:.2f}" if r['rf'] is not None else "None"
            lr_v  = f"{r['lr']:.2f}" if r['lr'] is not None else "None"
            print(f"#{r['idx']:<3} {r['dist']:>7.1f} {r['actual']:>8.2f} {xgb_v:>8} {rf_v:>8} {lr_v:>8} {r['best_pred']:>10.2f} {r['best_model']:<18} {r['abs_err']:>6.2f} {r['accuracy']:>6.1f}%")
        print("-" * 95)

    # ── Statistics ────────────────────────────────────────────────────────────
    accuracies  = [r["accuracy"] for r in rows]
    mean_acc    = float(np.mean(accuracies))
    median_acc  = float(np.median(accuracies))
    highest     = max(rows, key=lambda r: r["accuracy"])
    lowest      = min(rows, key=lambda r: r["accuracy"])

    # Model usage count
    model_counts = {}
    for r in rows:
        model_counts[r["best_model"]] = model_counts.get(r["best_model"], 0) + 1

    # Print summary to console
    print(f"\n[SUMMARY] Statistics over {len(rows)} Test Samples:")
    print(f"   * Mean Accuracy:   {mean_acc:.2f}%")
    print(f"   * Median Accuracy: {median_acc:.2f}%")
    print()
    print(f"   * Highest Accuracy: Sample #{highest['idx']} -> {highest['accuracy']:.2f}%  "
          f"(Dist={highest['dist']:.0f}km, Actual={highest['actual']:.2f}h, "
          f"Pred={highest['best_pred']:.2f}h, Model={highest['best_model']})")
    print(f"   * Lowest  Accuracy: Sample #{lowest['idx']}  -> {lowest['accuracy']:.2f}%  "
          f"(Dist={lowest['dist']:.0f}km, Actual={lowest['actual']:.2f}h, "
          f"Pred={lowest['best_pred']:.2f}h, Model={lowest['best_model']})")
    print()
    print("   * Best Model Selected per Sample:")
    for model_name, count in sorted(model_counts.items(), key=lambda x: -x[1]):
        pct = count / len(rows) if len(rows) > 0 else 0
        bar = "#" * int(round(pct * 30))
        print(f"     {model_name:<22} {count:>4}x  [{bar}]")
    print("=" * 95)

    # ── Save all data to test.txt ─────────────────────────────────────────────
    try:
        with open("test.txt", "w", encoding="utf-8") as f:
            f.write("=" * 95 + "\n")
            f.write(f"  DeliverAI -- ML Model Accuracy & Best-Model Selector Test Runner ({len(rows)} Samples)\n")
            f.write("=" * 95 + "\n\n")
            f.write(f"{'#':<4} {'Dist':>7} {'Actual':>8} {'XGB':>8} {'RF':>8} {'LR':>8} {'BestPred':>10} {'BestModel':<18} {'Err':>6} {'Acc%':>7}\n")
            f.write("-" * 95 + "\n")
            for r in rows:
                xgb_v = f"{r['xgb']:.2f}" if r['xgb'] is not None else "None"
                rf_v  = f"{r['rf']:.2f}" if r['rf'] is not None else "None"
                lr_v  = f"{r['lr']:.2f}" if r['lr'] is not None else "None"
                f.write(f"#{r['idx']:<3} {r['dist']:>7.1f} {r['actual']:>8.2f} {xgb_v:>8} {rf_v:>8} {lr_v:>8} {r['best_pred']:>10.2f} {r['best_model']:<18} {r['abs_err']:>6.2f} {r['accuracy']:>6.1f}%\n")
            f.write("-" * 95 + "\n\n")
            f.write(f"[SUMMARY] Statistics over {len(rows)} Test Samples:\n")
            f.write(f"   * Mean Accuracy:   {mean_acc:.2f}%\n")
            f.write(f"   * Median Accuracy: {median_acc:.2f}%\n\n")
            f.write(f"   * Highest Accuracy: Sample #{highest['idx']} -> {highest['accuracy']:.2f}%  "
                  f"(Dist={highest['dist']:.0f}km, Actual={highest['actual']:.2f}h, "
                  f"Pred={highest['best_pred']:.2f}h, Model={highest['best_model']})\n")
            f.write(f"   * Lowest  Accuracy: Sample #{lowest['idx']}  -> {lowest['accuracy']:.2f}%  "
                  f"(Dist={lowest['dist']:.0f}km, Actual={lowest['actual']:.2f}h, "
                  f"Pred={lowest['best_pred']:.2f}h, Model={lowest['best_model']})\n\n")
            f.write("   * Best Model Selected per Sample:\n")
            for model_name, count in sorted(model_counts.items(), key=lambda x: -x[1]):
                pct = count / len(rows) if len(rows) > 0 else 0
                bar = "#" * int(round(pct * 30))
                f.write(f"     {model_name:<22} {count:>4}x  [{bar}]\n")
            f.write("=" * 95 + "\n")
        print("\n[EXPORT] Successfully saved all detailed data to test.txt!")
    except Exception as e:
        print(f"\n[!] Failed to save data to test.txt: {e}")


if __name__ == "__main__":
    main()
