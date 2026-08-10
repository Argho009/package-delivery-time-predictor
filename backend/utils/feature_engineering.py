"""
utils/feature_engineering.py
Converts raw delivery inputs into the numeric feature vector used by ML models.
Updated to work with real Kaggle datasets (NO weather features in ML model).
Weather is still fetched from OpenWeather API for display, but NOT used as ML input.
"""

import numpy as np

# ── Encoding maps (must match training-time encoding) ────────────
TRAFFIC_LEVEL_MAP = {"LOW": 0, "MODERATE": 1, "HIGH": 2, "SEVERE": 3}

PACKAGE_TYPE_MAP = {"SMALL": 0, "MEDIUM": 1, "LARGE": 2, "FRAGILE": 3, "PERISHABLE": 4}
PRIORITY_MAP     = {"STANDARD": 0, "EXPRESS": 1, "OVERNIGHT": 2}
SHIPPING_MODE_MAP = {"ROAD": 0, "AIR": 1, "RAIL": 2, "SEA": 3}

# Feature order (must match training DataFrame columns exactly)
FEATURE_COLUMNS = [
    "distance_km",
    "traffic_duration_min",
    "traffic_level_enc",
    "package_weight_kg",
    "package_type_enc",
    "priority_enc",
    "shipping_mode_enc",
]

# NOTE: Weather features removed from ML model since Kaggle datasets
# don't have weather. Weather from OpenWeather API is shown in UI only.


def build_feature_vector(
    distance_km: float,
    traffic_duration_min: float,
    traffic_level: str,
    package_weight_kg: float,
    package_type: str,
    priority: str,
    shipping_mode: str = "ROAD",
) -> np.ndarray:
    """
    Build a 1×N feature array ready for model.predict().

    Returns:
        np.ndarray of shape (1, len(FEATURE_COLUMNS))
    """
    vector = [
        float(distance_km),
        float(traffic_duration_min),
        float(TRAFFIC_LEVEL_MAP.get(traffic_level.upper(), 1)),
        float(package_weight_kg),
        float(PACKAGE_TYPE_MAP.get(package_type.upper(), 1)),
        float(PRIORITY_MAP.get(priority.upper(), 0)),
        float(SHIPPING_MODE_MAP.get(shipping_mode.upper(), 0)),
    ]
    return np.array([vector], dtype=np.float64)


def dataframe_features(df):
    """
    Add encoded columns to a pandas DataFrame (used during training).
    Accepts both DB-sourced DataFrames and processed CSV DataFrames.
    Returns DataFrame with only FEATURE_COLUMNS.
    """
    df = df.copy()

    # Handle pre-encoded columns (from unified_delivery.csv)
    if "traffic_level_enc" in df.columns:
        pass  # already encoded
    elif "traffic_level" in df.columns:
        df["traffic_level_enc"] = df["traffic_level"].map(TRAFFIC_LEVEL_MAP).fillna(1)

    if "package_type_enc" in df.columns:
        pass
    elif "package_type" in df.columns:
        df["package_type_enc"] = df["package_type"].map(PACKAGE_TYPE_MAP).fillna(1)

    if "priority_enc" in df.columns:
        pass
    elif "priority" in df.columns:
        df["priority_enc"] = df["priority"].map(PRIORITY_MAP).fillna(0)

    if "shipping_mode_enc" not in df.columns:
        df["shipping_mode_enc"] = 0  # default ROAD

    # Ensure all columns present and numeric
    for col in FEATURE_COLUMNS:
        if col not in df.columns:
            df[col] = 0
        df[col] = df[col].fillna(0).astype(float)

    return df[FEATURE_COLUMNS]
