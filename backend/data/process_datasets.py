"""
data/process_datasets.py — Clean, normalize, and merge all 5 Tier 1 datasets
into a single unified CSV: data/processed/unified_delivery.csv

Column contract for output CSV:
    distance_km          float   — route distance
    traffic_duration_min float   — estimated duration with traffic
    traffic_level_enc    int     — 0=LOW,1=MOD,2=HIGH,3=SEVERE
    package_weight_kg    float   — weight
    package_type_enc     int     — 0=SMALL,1=MED,2=LARGE,3=FRAGILE,4=PERISH
    priority_enc         int     — 0=STANDARD,1=EXPRESS,2=OVERNIGHT
    shipping_mode_enc    int     — 0=ROAD,1=AIR,2=RAIL,3=SEA
    actual_time_hours    float   ← TARGET VARIABLE
    source               str     — which dataset row came from

Run from backend/ directory:
    python -m data.process_datasets
"""

import os
import glob
import math
import random
import numpy as np
import pandas as pd

RAW_DIR  = os.path.join(os.path.dirname(__file__), "raw")
OUT_DIR  = os.path.join(os.path.dirname(__file__), "processed")
OUT_FILE = os.path.join(OUT_DIR, "unified_delivery.csv")

os.makedirs(OUT_DIR, exist_ok=True)

random.seed(42)
np.random.seed(42)

# ── Helper: infer traffic level from congestion score ────────────
def congestion_to_traffic(score):
    """score 0-10 → traffic_level_enc"""
    if score < 3:   return 0   # LOW
    if score < 6:   return 1   # MODERATE
    if score < 8:   return 2   # HIGH
    return 3                    # SEVERE

# ── Helper: shipping mode string → enc ───────────────────────────
SHIP_MODE_MAP = {
    "road": 0, "truck": 0, "ground": 0, "standard": 0,
    "air": 1, "flight": 1, "first class": 1,
    "rail": 2, "train": 2, "second class": 2,
    "sea": 3, "ship": 3, "same day": 1,
}
def map_ship_mode(val):
    if pd.isna(val): return 0
    return SHIP_MODE_MAP.get(str(val).strip().lower(), 0)

# ── Helper: weight description → numeric ─────────────────────────
def weight_to_pkg_type(kg):
    if kg <= 2:    return 0   # SMALL
    if kg <= 10:   return 1   # MEDIUM
    if kg <= 50:   return 2   # LARGE
    return 2

# ── Helper: priority string → enc ────────────────────────────────
PRIORITY_MAP = {
    "standard": 0, "normal": 0, "low": 0,
    "medium": 0, "moderate": 0,
    "express": 1, "high": 1, "urgent": 1, "fast": 1,
    "overnight": 2, "critical": 2, "same day": 2,
}
def map_priority(val):
    if pd.isna(val): return 0
    return PRIORITY_MAP.get(str(val).strip().lower(), 0)

# ── Helper: add realistic noise to time ─────────────────────────
def add_noise(arr, pct=0.08):
    return arr * (1 + np.random.uniform(-pct, pct, size=len(arr)))

# ── Helper: find first CSV in a directory ───────────────────────
def find_csvs(slug):
    pattern = os.path.join(RAW_DIR, slug, "**", "*.csv")
    files = glob.glob(pattern, recursive=True)
    return files


# ════════════════════════════════════════════════════════════════
# Dataset 1 — Amazon Delivery Dataset
# Key columns: Distance (km), Order_Date, Delivery_Date,
#   Weather_Conditions, Road_Traffic_Density,
#   Delivery_person_Ratings, multiple_deliveries
#   Time_taken(min) ← TARGET
# ════════════════════════════════════════════════════════════════
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 # Radius of earth in kilometers
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2.0)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

def process_amazon(slug="amazon_delivery") -> pd.DataFrame:
    csvs = find_csvs(slug)
    if not csvs:
        print(f"[process] ⚠️  No CSVs found for {slug} — skipping.")
        return pd.DataFrame()

    dfs = [pd.read_csv(f) for f in csvs]
    df = pd.concat(dfs, ignore_index=True)
    df.columns = df.columns.str.strip()
    print(f"[process] Amazon raw shape: {df.shape}, cols: {list(df.columns)}")

    col_map = {}
    for c in df.columns:
        cl = c.lower().replace(" ", "_").replace("(", "").replace(")", "")
        col_map[c] = cl
    df.rename(columns=col_map, inplace=True)

    out = pd.DataFrame()

    # Calculate distance using lat/lng if available
    lat1_col = next((c for c in df.columns if "store_lat" in c or "pickup_lat" in c), None)
    lon1_col = next((c for c in df.columns if "store_lng" in c or "store_lon" in c or "pickup_lng" in c), None)
    lat2_col = next((c for c in df.columns if "drop_lat" in c or "delivery_lat" in c), None)
    lon2_col = next((c for c in df.columns if "drop_lng" in c or "drop_lon" in c or "delivery_lng" in c), None)

    if lat1_col and lon1_col and lat2_col and lon2_col:
        l1 = pd.to_numeric(df[lat1_col], errors="coerce").fillna(0)
        ln1 = pd.to_numeric(df[lon1_col], errors="coerce").fillna(0)
        l2 = pd.to_numeric(df[lat2_col], errors="coerce").fillna(0)
        ln2 = pd.to_numeric(df[lon2_col], errors="coerce").fillna(0)
        dist = haversine(l1, ln1, l2, ln2)
        dist = np.where((dist < 0.1) | (dist > 500), np.random.uniform(3, 45, len(df)), dist)
        out["distance_km"] = dist
    else:
        out["distance_km"] = np.random.uniform(5, 50, len(df))

    # Target: Delivery_Time or Time_taken(min) → hours
    time_col = next((c for c in df.columns if "delivery_time" in c or "time_taken" in c), None)
    if time_col:
        # Extract numeric minutes
        t_raw = df[time_col].astype(str).str.extract(r'(\d+)')[0]
        t_min = pd.to_numeric(t_raw, errors="coerce").fillna(30)
        out["actual_time_hours"] = (t_min / 60.0).clip(0.25, 24.0)
    else:
        out["actual_time_hours"] = (out["distance_km"] / 25.0 * np.random.uniform(0.8, 1.4, len(df))).clip(0.25, 24.0)

    # Traffic level from Traffic/Road_Traffic_Density
    traf_col = next((c for c in df.columns if "traffic" in c), None)
    if traf_col:
        traf_map = {"low": 0, "medium": 1, "high": 2, "jam": 3}
        out["traffic_level_enc"] = df[traf_col].astype(str).str.strip().str.lower().map(traf_map).fillna(1).astype(int)
    else:
        out["traffic_level_enc"] = np.random.choice([0,1,2,3], len(df), p=[0.25,0.40,0.25,0.10])

    traffic_mult = out["traffic_level_enc"].map({0:1.05,1:1.30,2:1.65,3:2.10})
    out["traffic_duration_min"] = (out["distance_km"] / 40.0 * 60) * traffic_mult

    out["package_weight_kg"] = np.random.uniform(0.5, 15.0, len(df))
    out["package_type_enc"]  = out["package_weight_kg"].apply(weight_to_pkg_type)
    out["priority_enc"]      = np.random.choice([0, 1, 2], len(df), p=[0.7, 0.2, 0.1])
    out["shipping_mode_enc"] = 0 # Road
    out["source"]            = "amazon_delivery"
    return out


# ════════════════════════════════════════════════════════════════
# Dataset 2 — Logistics & Supply Chain (Southern California)
# Key columns: Traffic_Congestion_Level, Lead_Time (days),
#   ETA_Variation (hours), Shipping_Costs,
#   Loading/Unloading_Time,  Delivery_Time_Deviation ← TARGET
# ════════════════════════════════════════════════════════════════
def process_logistics_supply_chain(slug="logistics_supply_chain") -> pd.DataFrame:
    csvs = find_csvs(slug)
    if not csvs:
        print(f"[process] ⚠️  No CSVs found for {slug} — skipping.")
        return pd.DataFrame()

    dfs = [pd.read_csv(f) for f in csvs]
    df = pd.concat(dfs, ignore_index=True)
    df.columns = df.columns.str.strip()
    print(f"[process] LogisticsSupply raw shape: {df.shape}, cols: {list(df.columns)}")

    col_map = {c: c.lower().replace(" ", "_").replace("/","_").replace("(","").replace(")","")
               for c in df.columns}
    df.rename(columns=col_map, inplace=True)

    out = pd.DataFrame()

    # Lead time (days) → hours as proxy for distance-equivalent travel
    lead_col = next((c for c in df.columns if "lead_time" in c), None)
    if lead_col:
        lead_days = pd.to_numeric(df[lead_col], errors="coerce").fillna(3)
        # Rough distance from lead time: ~500 km/day at 60 km/h
        out["distance_km"] = lead_days * 500 * np.random.uniform(0.4, 1.2, len(df))
    else:
        out["distance_km"] = np.random.uniform(100, 2000, len(df))

    # Target: Delivery_Time_Deviation (hours offset) + base Lead_Time hours
    dev_col = next((c for c in df.columns if "delivery_time_deviation" in c or "eta_variation" in c), None)
    if dev_col and lead_col:
        base_hours = pd.to_numeric(df[lead_col], errors="coerce").fillna(3) * 24
        deviation  = pd.to_numeric(df[dev_col], errors="coerce").fillna(0)
        out["actual_time_hours"] = (base_hours + deviation).clip(lower=0.5)
    elif lead_col:
        out["actual_time_hours"] = pd.to_numeric(df[lead_col], errors="coerce").fillna(3) * 24
    else:
        out["actual_time_hours"] = np.random.uniform(2, 120, len(df))

    # Traffic from congestion level (0-10 scale)
    cong_col = next((c for c in df.columns if "congestion" in c or "traffic" in c), None)
    if cong_col:
        out["traffic_level_enc"] = pd.to_numeric(df[cong_col], errors="coerce").fillna(5).apply(congestion_to_traffic)
    else:
        out["traffic_level_enc"] = np.random.choice([0,1,2,3], len(df))

    traffic_mult = out["traffic_level_enc"].map({0:1.05,1:1.30,2:1.65,3:2.10})
    out["traffic_duration_min"] = (out["distance_km"] / 50.0 * 60) * traffic_mult

    # Weight proxy from shipping costs
    cost_col = next((c for c in df.columns if "shipping_cost" in c), None)
    if cost_col:
        costs = pd.to_numeric(df[cost_col], errors="coerce").fillna(50)
        out["package_weight_kg"] = (costs / 5).clip(0.5, 100)  # rough: $5/kg
    else:
        out["package_weight_kg"] = np.random.uniform(1, 50, len(df))

    out["package_type_enc"]  = out["package_weight_kg"].apply(weight_to_pkg_type)
    out["priority_enc"]      = np.random.choice([0,1,2], len(df), p=[0.6,0.3,0.1])
    out["shipping_mode_enc"] = np.random.choice([0,1,2,3], len(df), p=[0.5,0.2,0.2,0.1])
    out["source"]            = "logistics_supply_chain"
    return out


# ════════════════════════════════════════════════════════════════
# Dataset 3 — Global Superstore Sales & Logistics
# Key columns: Order Date, Ship Date, Ship Mode, Sales,
#   Quantity, Region, Country, Postal Code
#   Ship Date - Order Date → actual delivery days → hours
# ════════════════════════════════════════════════════════════════
def process_global_superstore(slug="global_superstore") -> pd.DataFrame:
    csvs = find_csvs(slug)
    if not csvs:
        print(f"[process] ⚠️  No CSVs found for {slug} — skipping.")
        return pd.DataFrame()

    dfs = []
    for f in csvs:
        try:
            dfs.append(pd.read_csv(f, encoding="latin1"))
        except Exception:
            dfs.append(pd.read_csv(f, encoding="utf-8", errors="ignore"))

    df = pd.concat(dfs, ignore_index=True)
    df.columns = df.columns.str.strip()
    print(f"[process] GlobalSuperstore raw shape: {df.shape}, cols: {list(df.columns)}")

    col_map = {c: c.lower().replace(" ", "_") for c in df.columns}
    df.rename(columns=col_map, inplace=True)

    out = pd.DataFrame()

    # Target: Ship_Date - Order_Date in days → hours
    ord_col  = next((c for c in df.columns if "order_date" in c or "order date" in c), None)
    ship_col = next((c for c in df.columns if "ship_date" in c or "ship date" in c), None)

    if ord_col and ship_col:
        df[ord_col]  = pd.to_datetime(df[ord_col],  errors="coerce", dayfirst=True)
        df[ship_col] = pd.to_datetime(df[ship_col], errors="coerce", dayfirst=True)
        delta_days   = (df[ship_col] - df[ord_col]).dt.total_seconds() / 86400
        out["actual_time_hours"] = (delta_days * 24).clip(lower=1, upper=168)
    else:
        out["actual_time_hours"] = np.random.uniform(24, 120, len(df))

    # Ship mode → shipping_mode_enc + priority_enc
    mode_col = next((c for c in df.columns if "ship_mode" in c), None)
    if mode_col:
        out["shipping_mode_enc"] = df[mode_col].apply(map_ship_mode)
        out["priority_enc"]      = df[mode_col].apply(map_priority)
    else:
        out["shipping_mode_enc"] = 0
        out["priority_enc"]      = 0

    # Distance approximation from region/country (rough km by segment)
    seg_col = next((c for c in df.columns if "segment" in c or "region" in c), None)
    if seg_col:
        region_dist = {
            "consumer": 500, "corporate": 800, "home office": 300,
            "west": 1200, "east": 900, "central": 700, "south": 600,
        }
        out["distance_km"] = df[seg_col].str.strip().str.lower().map(region_dist).fillna(700)
        out["distance_km"] += np.random.uniform(-200, 200, len(df))
        out["distance_km"] = out["distance_km"].clip(50)
    else:
        out["distance_km"] = np.random.uniform(100, 2000, len(df))

    out["traffic_level_enc"]    = np.random.choice([0,1,2,3], len(df), p=[0.25,0.40,0.25,0.10])
    traffic_mult = out["traffic_level_enc"].map({0:1.05,1:1.30,2:1.65,3:2.10})
    out["traffic_duration_min"] = (out["distance_km"] / 50.0 * 60) * traffic_mult

    # Weight from sales/quantity
    qty_col  = next((c for c in df.columns if "quantity" in c), None)
    sale_col = next((c for c in df.columns if "sales" in c), None)
    if qty_col:
        out["package_weight_kg"] = pd.to_numeric(df[qty_col], errors="coerce").fillna(2) * 1.5
    elif sale_col:
        out["package_weight_kg"] = (pd.to_numeric(df[sale_col], errors="coerce").fillna(100) / 50).clip(0.5, 50)
    else:
        out["package_weight_kg"] = np.random.uniform(0.5, 20, len(df))

    out["package_type_enc"] = out["package_weight_kg"].apply(weight_to_pkg_type)
    out["source"]           = "global_superstore"
    return out


# ════════════════════════════════════════════════════════════════
# Dataset 4 — E-Commerce Shipment Prediction
# Key columns: Warehouse_block, Mode_of_Shipment, Customer_rating,
#   Cost_of_the_Product, Product_importance,
#   Discount_offered, Weight_in_gms, Reached.on.Time_Y.N ← TARGET
# Note: Target is binary (on-time or not); we synthesize delivery
#       hours from distance + ship mode + on-time flag.
# ════════════════════════════════════════════════════════════════
def process_ecom_shipment(slug="ecom_shipment") -> pd.DataFrame:
    csvs = find_csvs(slug)
    if not csvs:
        print(f"[process] ⚠️  No CSVs found for {slug} — skipping.")
        return pd.DataFrame()

    dfs = [pd.read_csv(f) for f in csvs]
    df = pd.concat(dfs, ignore_index=True)
    df.columns = df.columns.str.strip()
    print(f"[process] EcomShipment raw shape: {df.shape}, cols: {list(df.columns)}")

    col_map = {c: c.lower().replace(" ", "_").replace(".", "_") for c in df.columns}
    df.rename(columns=col_map, inplace=True)

    out = pd.DataFrame()

    # Weight (in grams → kg)
    wt_col = next((c for c in df.columns if "weight" in c), None)
    if wt_col:
        wt_raw = pd.to_numeric(df[wt_col], errors="coerce").fillna(2000)
        # If max > 1000, assume grams
        if wt_raw.max() > 500:
            out["package_weight_kg"] = (wt_raw / 1000).clip(0.1, 100)
        else:
            out["package_weight_kg"] = wt_raw.clip(0.1, 100)
    else:
        out["package_weight_kg"] = np.random.uniform(0.5, 15, len(df))

    # Ship mode
    mode_col = next((c for c in df.columns if "mode" in c or "shipment" in c), None)
    if mode_col:
        out["shipping_mode_enc"] = df[mode_col].apply(map_ship_mode)
    else:
        out["shipping_mode_enc"] = 0

    # Priority from product_importance
    imp_col = next((c for c in df.columns if "importance" in c), None)
    if imp_col:
        out["priority_enc"] = df[imp_col].apply(map_priority)
    else:
        out["priority_enc"] = 0

    # Distance from ship mode (proxy)
    mode_dist = {0: 800, 1: 2000, 2: 1500, 3: 3000}
    out["distance_km"] = out["shipping_mode_enc"].map(mode_dist)
    out["distance_km"] += np.random.uniform(-300, 300, len(df))
    out["distance_km"] = out["distance_km"].clip(50)

    # Traffic level
    out["traffic_level_enc"] = np.random.choice([0,1,2,3], len(df), p=[0.25,0.40,0.25,0.10])
    traffic_mult = out["traffic_level_enc"].map({0:1.05,1:1.30,2:1.65,3:2.10})
    out["traffic_duration_min"] = (out["distance_km"] / 50.0 * 60) * traffic_mult

    # Target: synthesize from distance + on-time flag
    # Ship speed by mode (km/h effective): road=50, air=400, rail=120, sea=30
    mode_speed = {0: 50, 1: 400, 2: 120, 3: 30}
    speed = out["shipping_mode_enc"].map(mode_speed)
    base_hours = out["distance_km"] / speed

    on_time_col = next((c for c in df.columns
                        if "reached" in c or "on_time" in c or "reached_on_time" in c), None)
    if on_time_col:
        on_time = pd.to_numeric(df[on_time_col], errors="coerce").fillna(1)
        # on_time=1 → delivered ~on-schedule; 0 → +20-60% delay
        delay_mult = np.where(on_time == 1,
                              np.random.uniform(0.90, 1.05, len(df)),
                              np.random.uniform(1.20, 1.65, len(df)))
        out["actual_time_hours"] = (base_hours * delay_mult * traffic_mult).clip(lower=0.25)
    else:
        out["actual_time_hours"] = (base_hours * np.random.uniform(0.85,1.20,len(df))).clip(lower=0.25)

    out["package_type_enc"] = out["package_weight_kg"].apply(weight_to_pkg_type)
    out["source"]           = "ecom_shipment"
    return out


# ════════════════════════════════════════════════════════════════
# Dataset 5 — Enhanced Superstore Sales Dataset
# Key columns: Order Date, Ship Date, Ship Mode,
#   Sales, Quantity, Region, Sub-Category
# Target: Ship_Date - Order_Date days → hours
# ════════════════════════════════════════════════════════════════
def process_enhanced_superstore(slug="enhanced_superstore") -> pd.DataFrame:
    csvs = find_csvs(slug)
    if not csvs:
        print(f"[process] ⚠️  No CSVs found for {slug} — skipping.")
        return pd.DataFrame()

    dfs = []
    for f in csvs:
        try:
            dfs.append(pd.read_csv(f, encoding="latin1"))
        except Exception:
            dfs.append(pd.read_csv(f, encoding="utf-8", errors="ignore"))

    df = pd.concat(dfs, ignore_index=True)
    df.columns = df.columns.str.strip()
    print(f"[process] EnhancedSuperstore raw shape: {df.shape}, cols: {list(df.columns)}")

    col_map = {c: c.lower().replace(" ", "_").replace("-","_") for c in df.columns}
    df.rename(columns=col_map, inplace=True)

    out = pd.DataFrame()

    # Target: Order-to-Ship days → hours
    ord_col  = next((c for c in df.columns if "order_date" in c), None)
    ship_col = next((c for c in df.columns if "ship_date" in c), None)

    if ord_col and ship_col:
        df[ord_col]  = pd.to_datetime(df[ord_col],  errors="coerce", dayfirst=True)
        df[ship_col] = pd.to_datetime(df[ship_col], errors="coerce", dayfirst=True)
        delta = (df[ship_col] - df[ord_col]).dt.total_seconds() / 3600
        out["actual_time_hours"] = delta.clip(lower=1)
    else:
        out["actual_time_hours"] = np.random.uniform(24, 168, len(df))

    # Ship mode → priority & mode
    mode_col = next((c for c in df.columns if "ship_mode" in c), None)
    if mode_col:
        out["shipping_mode_enc"] = df[mode_col].apply(map_ship_mode)
        out["priority_enc"]      = df[mode_col].apply(map_priority)
    else:
        out["shipping_mode_enc"] = 0
        out["priority_enc"]      = 0

    # Distance from region
    reg_col = next((c for c in df.columns if "region" in c), None)
    if reg_col:
        region_dist = {"west":1200,"east":900,"central":700,"south":600,"north":1000}
        out["distance_km"] = df[reg_col].str.strip().str.lower().map(region_dist).fillna(800)
        out["distance_km"] += np.random.uniform(-200, 200, len(df))
    else:
        out["distance_km"] = np.random.uniform(100, 2000, len(df))

    out["traffic_level_enc"] = np.random.choice([0,1,2,3], len(df), p=[0.25,0.40,0.25,0.10])
    traffic_mult = out["traffic_level_enc"].map({0:1.05,1:1.30,2:1.65,3:2.10})
    out["traffic_duration_min"] = (out["distance_km"] / 50.0 * 60) * traffic_mult

    qty_col = next((c for c in df.columns if "quantity" in c), None)
    if qty_col:
        out["package_weight_kg"] = pd.to_numeric(df[qty_col], errors="coerce").fillna(2) * 1.5
    else:
        out["package_weight_kg"] = np.random.uniform(0.5, 20, len(df))

    out["package_type_enc"] = out["package_weight_kg"].apply(weight_to_pkg_type)
    out["source"]           = "enhanced_superstore"
    return out


CITY_PAIRS = [
    ("Mumbai", "Delhi"), ("Bangalore", "Chennai"), ("Hyderabad", "Pune"),
    ("Kolkata", "Patna"), ("Ahmedabad", "Jaipur"), ("Surat", "Mumbai"),
    ("New York", "Chicago"), ("San Francisco", "Seattle"), ("Los Angeles", "Las Vegas"),
    ("London", "Paris"), ("Dubai", "Riyadh"), ("Tokyo", "Osaka"),
    ("Singapore", "Kuala Lumpur"), ("Berlin", "Amsterdam"), ("Sydney", "Melbourne")
]

# ── Final merge & clean ──────────────────────────────────────────
PROCESSORS = [
    process_amazon,
    process_logistics_supply_chain,
    process_global_superstore,
    process_ecom_shipment,
    process_enhanced_superstore,
]

REQUIRED_COLS = [
    "tracking_id", "origin_city", "destination_city",
    "distance_km", "traffic_duration_min", "traffic_level_enc",
    "package_weight_kg", "package_type_enc", "priority_enc",
    "shipping_mode_enc", "actual_time_hours", "source",
]


def main():
    print("=" * 60)
    print("  AI Delivery Prediction — Dataset Processor")
    print("=" * 60)

    parts = []
    for proc in PROCESSORS:
        try:
            df = proc()
            if df.empty:
                continue

            # Assign real city pairs and unique tracking IDs if missing
            n_rows = len(df)
            city_idx = np.random.randint(0, len(CITY_PAIRS), size=n_rows)
            df["origin_city"]      = [CITY_PAIRS[i][0] for i in city_idx]
            df["destination_city"] = [CITY_PAIRS[i][1] for i in city_idx]
            df["tracking_id"]       = [f"PKG{proc.__name__[8:11].upper()}{i+1:06d}" for i in range(n_rows)]

            # Ensure all required columns exist
            for col in REQUIRED_COLS:
                if col not in df.columns:
                    df[col] = 0
            df = df[REQUIRED_COLS]
            parts.append(df)
            print(f"[process] ✅ {proc.__name__}: {len(df)} rows")
        except Exception as e:
            print(f"[process] ❌ {proc.__name__} failed: {e}")
            import traceback; traceback.print_exc()

    if not parts:
        print("[process] ❌ No datasets processed. Run download_datasets.py first.")
        return

    unified = pd.concat(parts, ignore_index=True)

    # ── Clean ────────────────────────────────────────────────────
    before = len(unified)
    unified = unified.dropna(subset=["actual_time_hours", "distance_km"])
    unified = unified[unified["actual_time_hours"] > 0]
    unified = unified[unified["distance_km"] > 0]

    # Cap outliers (actual_time_hours max 168h / 7 days, distance max 3000km)
    unified["actual_time_hours"] = unified["actual_time_hours"].clip(lower=0.25, upper=168.0)
    unified["distance_km"]       = unified["distance_km"].clip(lower=1.0, upper=3000.0)
    unified["traffic_duration_min"] = (unified["distance_km"] / 50.0 * 60) * unified["traffic_level_enc"].map({0:1.05,1:1.30,2:1.65,3:2.10})
    unified["package_weight_kg"] = unified["package_weight_kg"].clip(lower=0.1, upper=100.0)

    unified = unified.reset_index(drop=True)
    after = len(unified)

    # ── Save ─────────────────────────────────────────────────────
    unified.to_csv(OUT_FILE, index=False)
    print(f"\n[process] 📊 Dataset Summary:")
    print(f"          Raw total:    {before:,}")
    print(f"          After clean:  {after:,}")
    print(f"          Sources: {unified['source'].value_counts().to_dict()}")
    print(f"          Cols:  {list(unified.columns)}")
    print(f"\n[process] ✅ Saved: {OUT_FILE}")
    print(f"[process] Next step: python -m data.load_to_db")

    return unified


if __name__ == "__main__":
    main()
