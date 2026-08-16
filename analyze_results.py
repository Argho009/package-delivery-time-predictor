#!/usr/bin/env python3
"""
analyze_results.py — Parses test.txt and performs deep statistical analysis
on ML models (XGBoost, Random Forest, Linear Regression).
"""

import os
import re
import pandas as pd
import numpy as np

def parse_val(v):
    if v is None or v == "None":
        return np.nan
    try:
        return float(v)
    except ValueError:
        return np.nan

def main():
    txt_path = "test.txt"
    report_path = "analysis_report.md"

    if not os.path.exists(txt_path):
        print(f"[-] Error: {txt_path} not found. Please run 'python test.py 10000' first.")
        return

    print(f"[+] Reading {txt_path}...")
    
    pattern = re.compile(
        r"^#(\d+)\s+"          # index
        r"([\d.]+)\s+"         # distance
        r"([\d.]+)\s+"         # actual hours
        r"(\S+)\s+"            # XGB pred
        r"(\S+)\s+"            # RF pred
        r"(\S+)\s+"            # LR pred
        r"([\d.]+)\s+"         # Best pred
        r"([a-zA-Z0-9_]+)\s+"  # Best model
        r"([\d.]+)\s+"         # Error
        r"([\d.-]+)%"          # Accuracy% (handle negative/dash if any)
    )

    data = []
    with open(txt_path, "r", encoding="utf-8") as f:
        for line in f:
            match = pattern.match(line.strip())
            if match:
                groups = match.groups()
                data.append({
                    "idx": int(groups[0]),
                    "distance_km": float(groups[1]),
                    "actual_hours": float(groups[2]),
                    "xgb_hours": parse_val(groups[3]),
                    "rf_hours": parse_val(groups[4]),
                    "lr_hours": parse_val(groups[5]),
                    "best_pred_hours": float(groups[6]),
                    "best_model": groups[7],
                    "abs_error_hours": float(groups[8]),
                    "accuracy_pct": float(groups[9]),
                })

    if not data:
        print("[-] Error: No matching prediction records found in test.txt.")
        return

    df = pd.DataFrame(data)
    total_samples = len(df)
    print(f"[+] Successfully parsed {total_samples:,} records.")

    # 1. Global Metrics
    mean_accuracy = df["accuracy_pct"].mean()
    median_accuracy = df["accuracy_pct"].median()
    mean_abs_error = df["abs_error_hours"].mean()
    rmse = np.sqrt((df["abs_error_hours"] ** 2).mean())
    
    # Model win rates
    win_counts = df["best_model"].value_counts()
    win_shares = df["best_model"].value_counts(normalize=True) * 100

    # 2. Distance Bins
    bins = [0, 50, 250, 1000, np.inf]
    labels = ["Local / Urban (<50 km)", "Short-Haul (50-250 km)", "Medium-Haul (250-1000 km)", "Long-Haul (>1000 km)"]
    df["distance_tier"] = pd.cut(df["distance_km"], bins=bins, labels=labels)

    tier_stats = []
    for label in labels:
        tier_df = df[df["distance_tier"] == label]
        if len(tier_df) == 0:
            continue
        
        tier_win_shares = tier_df["best_model"].value_counts(normalize=True) * 100
        dominant_model = tier_win_shares.index[0] if len(tier_win_shares) > 0 else "N/A"
        dominant_share = tier_win_shares.iloc[0] if len(tier_win_shares) > 0 else 0.0
        
        tier_stats.append({
            "Tier": label,
            "Count": len(tier_df),
            "Mean Acc": f"{tier_df['accuracy_pct'].mean():.2f}%",
            "Median Acc": f"{tier_df['accuracy_pct'].median():.2f}%",
            "MAE": f"{tier_df['abs_error_hours'].mean():.2f}h",
            "Dominant Model": f"{dominant_model} ({dominant_share:.1f}%)"
        })
    tier_summary_df = pd.DataFrame(tier_stats)

    # 2.5. 1km Binned Analysis
    max_distance = df["distance_km"].max()
    bin_size = 1.0
    df["dist_bin_idx"] = np.floor(df["distance_km"] / bin_size).astype(int)
    
    bin_groups = df.groupby("dist_bin_idx")
    bin_analysis = []
    
    for bin_idx, group in bin_groups:
        bin_start = bin_idx * bin_size
        bin_end = bin_start + bin_size
        bin_label = f"{int(bin_start)}-{int(bin_end)}"
        
        # Calculate dominant model based on lowest MAE in this bin to maximize accuracy
        model_errors = {}
        for m_name, col in [("xgboost", "xgb_hours"), ("random_forest", "rf_hours"), ("linear_regression", "lr_hours")]:
            valid_group = group.dropna(subset=[col])
            if len(valid_group) > 0:
                mae_val = (valid_group["actual_hours"] - valid_group[col]).abs().mean()
                model_errors[m_name] = mae_val
        
        if model_errors:
            dominant_model = min(model_errors, key=model_errors.get)
            bin_win_counts = group["best_model"].value_counts()
            dom_count = bin_win_counts.get(dominant_model, 0)
            dom_pct = (dom_count / len(group)) * 100
        else:
            dominant_model = "N/A"
            dom_pct = 0.0
            
        mean_acc = group["accuracy_pct"].mean()
        mae = group["abs_error_hours"].mean()
        
        bin_analysis.append({
            "bin_idx": bin_idx,
            "label": bin_label,
            "count": len(group),
            "mean_acc": mean_acc,
            "mae": mae,
            "dominant_model": dominant_model,
            "dominant_pct": dom_pct
        })
        
    bin_analysis.sort(key=lambda x: x["bin_idx"])

    # 3. Model Accuracy Comparison (when each model is compared directly)
    model_maes = {}
    model_rmses = {}
    for model_name, col in [("XGBoost", "xgb_hours"), ("Random Forest", "rf_hours"), ("Linear Regression", "lr_hours")]:
        valid_df = df.dropna(subset=[col])
        if len(valid_df) > 0:
            errors = (valid_df["actual_hours"] - valid_df[col]).abs()
            model_maes[model_name] = errors.mean()
            model_rmses[model_name] = np.sqrt((errors ** 2).mean())
        else:
            model_maes[model_name] = np.nan
            model_rmses[model_name] = np.nan

    # 4. Underperforming Cases (Accuracy < 70%)
    underperforming = df[df["accuracy_pct"] < 70.0]
    pct_underperforming = (len(underperforming) / total_samples) * 100

    # Build ASCII Terminal Dashboard
    dashboard = []
    dashboard.append("=" * 85)
    dashboard.append("  DELIVERAI — MODEL PREDICTION ANALYSIS DASHBOARD")
    dashboard.append("=" * 85)
    dashboard.append(f"  * Total Samples Analyzed:  {total_samples:,}")
    dashboard.append(f"  * Global Mean Accuracy:    {mean_accuracy:.2f}%")
    dashboard.append(f"  * Global Median Accuracy:  {median_accuracy:.2f}%")
    dashboard.append(f"  * Mean Absolute Error:     {mean_abs_error:.2f} hours")
    dashboard.append(f"  * Root Mean Sq. Error:     {rmse:.2f} hours")
    dashboard.append("-" * 85)
    dashboard.append("  MODEL SELECTION SHARE (Which model was closest to actual delivery time?):")
    for model, count in win_counts.items():
        pct = win_shares[model]
        bar = "#" * int(pct / 4)
        dashboard.append(f"    - {model:<18} : {count:>5}x ({pct:>5.2f}%) [{bar}]")
    dashboard.append("-" * 85)
    dashboard.append("  GEOSPATIAL PERFORMANCE BREAKDOWN:")
    dashboard.append(f"    {'Tier':<26} | {'Count':>6} | {'Mean Acc':>10} | {'Median Acc':>10} | {'MAE':>6} | {'Dominant Model'}")
    dashboard.append("    " + "-" * 78)
    for stat in tier_stats:
        dashboard.append(f"    {stat['Tier']:<26} | {stat['Count']:>6} | {stat['Mean Acc']:>10} | {stat['Median Acc']:>10} | {stat['MAE']:>6} | {stat['Dominant Model']}")
    dashboard.append("-" * 85)
    dashboard.append("  BEST PERFORMING MODEL PER 1 KM RANGE (Sample Bins):")
    dashboard.append(f"    {'Range (km)':<15} | {'Count':>6} | {'Mean Acc':>10} | {'MAE':>7} | {'Dominant Model'}")
    dashboard.append("    " + "-" * 65)
    
    visible_bins = [b for b in bin_analysis if b["count"] > 0]
    for b in visible_bins[:15]:
        dashboard.append(f"    {b['label']:<15} | {b['count']:>6} | {b['mean_acc']:>9.1f}% | {b['mae']:>6.2f}h | {b['dominant_model']} ({b['dominant_pct']:.1f}%)")
        
    if len(visible_bins) > 15:
        dashboard.append(f"    ... ({len(visible_bins) - 15} more non-empty bins generated, see analysis_report.md for full list)")
    dashboard.append("-" * 85)
    dashboard.append("  MODEL COMPARISON OVER ALL SAMPLES (Lower is better):")
    dashboard.append(f"    {'Model Name':<20} | {'MAE (Mean Abs Error)':<20} | {'RMSE (Root Mean Sq Error)':<25}")
    dashboard.append("    " + "-" * 69)
    for model_name in ["XGBoost", "Random Forest", "Linear Regression"]:
        dashboard.append(f"    {model_name:<20} | {model_maes[model_name]:>18.2f}h | {model_rmses[model_name]:>23.2f}h")
    dashboard.append("-" * 85)
    dashboard.append("  ERROR CONCENTRATION DIAGNOSIS:")
    dashboard.append(f"    - Underperforming predictions (Acc < 70%): {len(underperforming):,} samples ({pct_underperforming:.2f}%)")
    if len(underperforming) > 0:
        mean_dist_under = underperforming["distance_km"].mean()
        dashboard.append(f"    - Average distance of underperforming runs: {mean_dist_under:.1f} km")
        # Check if underperforming is concentrated in short distance
        local_under = len(underperforming[underperforming["distance_km"] < 50])
        dashboard.append(f"    - Local distance (<50 km) share of errors:  {(local_under/len(underperforming))*100:.2f}%")
    dashboard.append("=" * 85)

    print("\n".join(dashboard))

    # Save Markdown Report
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# DeliverAI ML Predictions Analysis Report\n\n")
        f.write(f"Generated automatically from `{txt_path}` containing **{total_samples:,}** prediction logs.\n\n")
        
        f.write("## 1. Global Performance Metrics\n\n")
        f.write("| Metric | Value |\n")
        f.write("| --- | --- |\n")
        f.write(f"| **Total Test Samples** | {total_samples:,} |\n")
        f.write(f"| **Mean Accuracy** | **{mean_accuracy:.2f}%** |\n")
        f.write(f"| **Median Accuracy** | **{median_accuracy:.2f}%** |\n")
        f.write(f"| **Mean Absolute Error (MAE)** | {mean_abs_error:.2f} hours |\n")
        f.write(f"| **Root Mean Squared Error (RMSE)** | {rmse:.2f} hours |\n\n")

        f.write("## 2. Model Selection Share\n")
        f.write("Percentage of runs where each model yielded the prediction closest to the actual time:\n\n")
        f.write("| Model | Best Selection Count | Share (%) |\n")
        f.write("| --- | --- | --- |\n")
        for model, count in win_counts.items():
            f.write(f"| **{model}** | {count:,} | {win_shares[model]:.2f}% |\n")
        f.write("\n")

        f.write("## 3. Geospatial Performance Breakdown\n\n")
        f.write("| Distance Tier | Sample Count | Mean Accuracy | Median Accuracy | MAE | Dominant Model |\n")
        f.write("| --- | --- | --- | --- | --- | --- |\n")
        for stat in tier_stats:
            f.write(f"| {stat['Tier']} | {stat['Count']:,} | {stat['Mean Acc']} | {stat['Median Acc']} | {stat['MAE']} | {stat['Dominant Model']} |\n")
        f.write("\n")

        f.write("## 4. Overall Model Error Comparison (Across all valid rows)\n\n")
        f.write("| Model | MAE | RMSE |\n")
        f.write("| --- | --- | --- |\n")
        for model_name in ["XGBoost", "Random Forest", "Linear Regression"]:
            f.write(f"| {model_name} | {model_maes[model_name]:.2f}h | {model_rmses[model_name]:.2f}h |\n")
        f.write("\n")

        f.write("## 5. Diagnostic Insights\n\n")
        f.write(f"* **Underperforming Runs (<70% Acc)**: {len(underperforming):,} of {total_samples:,} ({pct_underperforming:.2f}%)\n")
        if len(underperforming) > 0:
            f.write(f"* **Mean Distance of Underperforming Runs**: {mean_dist_under:.2f} km\n")
            f.write(f"* **Local Deliveries (<50 km) Concentration**: {local_under:,} runs ({ (local_under/len(underperforming))*100:.2f}% of all underperforming runs)\n")
            f.write("  > [!TIP]\n")
            f.write("  > High error concentration in local deliveries (< 50 km) is common since small traffic anomalies or dispatch delays represent a large relative percentage error for short trips. Enhancing local traffic features can improve short-haul accuracy.\n")
        f.write("\n")

        f.write("## 6. Detailed 1 km Range Performance Breakdown\n\n")
        f.write("Here is the best performing model (dominant model with the most wins) for every 1 km distance tier:\n\n")
        f.write("| Distance Tier (km) | Sample Count | Mean Accuracy | MAE (hours) | Dominant Model | Model Win Share (%) |\n")
        f.write("| --- | --- | --- | --- | --- | --- |\n")
        for b in visible_bins:
            f.write(f"| {b['label']} | {b['count']:,} | {b['mean_acc']:.2f}% | {b['mae']:.2f}h | {b['dominant_model']} | {b['dominant_pct']:.2f}% |\n")
        f.write("\n")

    print(f"\n[EXPORT] Detailed Markdown report exported successfully to: {report_path}")

    # Save to CSV
    csv_report_path = "range_performance_1km.csv"
    try:
        bins_df = pd.DataFrame(visible_bins)
        bins_df_clean = bins_df[[
            "label", "count", "mean_acc", "mae", "dominant_model", "dominant_pct"
        ]].rename(columns={
            "label": "Distance Tier (km)",
            "count": "Sample Count",
            "mean_acc": "Mean Accuracy (%)",
            "mae": "Mean Absolute Error (hours)",
            "dominant_model": "Dominant Model",
            "dominant_pct": "Model Win Share (%)"
        })
        bins_df_clean["Mean Accuracy (%)"] = bins_df_clean["Mean Accuracy (%)"].round(2)
        bins_df_clean["Mean Absolute Error (hours)"] = bins_df_clean["Mean Absolute Error (hours)"].round(2)
        bins_df_clean["Model Win Share (%)"] = bins_df_clean["Model Win Share (%)"].round(2)
        
        bins_df_clean.to_csv(csv_report_path, index=False)
        print(f"[EXPORT] Successfully saved 1km range breakdown to CSV: {csv_report_path}")
    except Exception as e:
        print(f"[!] Failed to save CSV: {e}")

if __name__ == "__main__":
    main()
