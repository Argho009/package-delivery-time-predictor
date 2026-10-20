"""
utils/sustainability.py — Logistics Carbon Footprint & Eco-Impact Estimator
Based on the Global Logistics Emissions Council (GLEC) Framework and DEFRA emission factors.
"""

# Emission factors in kg CO2 per ton-km
EMISSION_FACTORS_KG_PER_TON_KM = {
    "ROAD": 0.105,   # Average road freight (vans / medium trucks)
    "AIR": 0.602,    # Air express cargo (domestic / short-haul)
    "RAIL": 0.028,   # Electric / diesel rail freight
    "SEA": 0.015,    # Coastal / container ship cargo
}

# Baseline vehicle empty-run overhead per km (kg CO2)
VEHICLE_BASE_KG_PER_KM = {
    "ROAD": 0.045,
    "AIR": 0.220,
    "RAIL": 0.012,
    "SEA": 0.008,
}


def calculate_carbon_footprint(distance_km: float, package_weight_kg: float, shipping_mode: str = "ROAD") -> dict:
    """
    Calculate estimated carbon emissions (kg CO2) for a given shipment and compare across modes.
    """
    mode = shipping_mode.upper() if shipping_mode else "ROAD"
    if mode not in EMISSION_FACTORS_KG_PER_TON_KM:
        mode = "ROAD"

    weight_tons = max(float(package_weight_kg), 0.1) / 1000.0
    dist = max(float(distance_km), 1.0)

    factor = EMISSION_FACTORS_KG_PER_TON_KM[mode]
    base_overhead = VEHICLE_BASE_KG_PER_KM[mode] * dist

    co2_kg = round((weight_tons * dist * factor) + (base_overhead * min(weight_tons * 10, 1.0)), 2)
    # Ensure a non-zero reasonable value
    co2_kg = max(co2_kg, 0.05)

    # Road comparison baseline
    road_factor = EMISSION_FACTORS_KG_PER_TON_KM["ROAD"]
    road_co2 = round((weight_tons * dist * road_factor) + (VEHICLE_BASE_KG_PER_KM["ROAD"] * dist * min(weight_tons * 10, 1.0)), 2)

    # Air comparison baseline
    air_factor = EMISSION_FACTORS_KG_PER_TON_KM["AIR"]
    air_co2 = round((weight_tons * dist * air_factor) + (VEHICLE_BASE_KG_PER_KM["AIR"] * dist * min(weight_tons * 10, 1.0)), 2)

    savings_vs_air = round(max(air_co2 - co2_kg, 0.0), 2)

    # Eco Rating
    if mode in ["RAIL", "SEA"]:
        rating = "A+"
        label = "Ultra-Low Carbon"
        badge_color = "#10b981"
        tip = "Great choice! Rail & Sea produce up to 80% less emissions than Road."
    elif mode == "ROAD":
        rating = "B"
        label = "Standard Road Impact"
        badge_color = "#f59e0b"
        tip = f"Switching this shipment to Rail would reduce emissions by ~{round((1 - 0.028/0.105)*100)}%."
    else:  # AIR
        rating = "D"
        label = "High Speed / High Footprint"
        badge_color = "#ef4444"
        tip = "Air express delivers fastest but produces ~5.7x more CO2 than Road freight."

    trees_needed = round(co2_kg / 22.0, 3)

    return {
        "co2_kg": co2_kg,
        "mode": mode,
        "rating": rating,
        "rating_label": label,
        "badge_color": badge_color,
        "savings_vs_air_kg": savings_vs_air,
        "trees_offset_needed": trees_needed,
        "tip": tip,
    }
