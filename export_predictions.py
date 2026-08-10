"""
export_predictions.py — Exports historical and predicted delivery records from SQLite database to a clean CSV file
"""

import os
import sqlite3
import pandas as pd

DB_PATH  = os.path.join(os.path.dirname(__file__), "backend", "delivery.db")
OUT_CSV  = os.path.join(os.path.dirname(__file__), "past_predictions_and_history.csv")

def main():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT 
        tracking_id AS [Tracking ID],
        origin_city AS [Origin City],
        destination_city AS [Destination City],
        distance_km AS [Distance (km)],
        traffic_level AS [Traffic Level],
        package_weight_kg AS [Package Weight (kg)],
        package_type AS [Package Type],
        priority AS [Priority],
        predicted_time_hours AS [Predicted Time (Hours)],
        actual_time_hours AS [Actual Time (Hours)],
        model_used AS [ML Model Used],
        created_at AS [Timestamp]
    FROM delivery_records
    ORDER BY id DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    df.to_csv(OUT_CSV, index=False)
    print(f"[EXPORT] Successfully exported {len(df):,} delivery records & past predictions to:")
    print(f"         {OUT_CSV}")

if __name__ == "__main__":
    main()
