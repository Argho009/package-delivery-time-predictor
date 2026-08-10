"""
services/maps_service.py — OpenStreetMap / OSRM Routing Service
100% free, zero-key geospatial routing engine.
Uses Nominatim for geocoding and OSRM for driving route calculation.
"""

import requests
import logging

logger = logging.getLogger(__name__)

NOMINATIM_URL  = "https://nominatim.openstreetmap.org/search"
OSRM_ROUTE_URL = "http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}"

HEADERS = {
    "User-Agent": "DeliverAI-Package-Delivery-Prediction-System/1.0"
}

# Traffic level thresholds based on duration multipliers
TRAFFIC_THRESHOLDS = {
    "LOW":      (0.0,  1.15),
    "MODERATE": (1.15, 1.45),
    "HIGH":     (1.45, 1.80),
    "SEVERE":   (1.80, float("inf")),
}


def _classify_traffic(base_seconds: float, traffic_seconds: float) -> str:
    if base_seconds == 0:
        return "MODERATE"
    ratio = traffic_seconds / base_seconds
    for level, (low, high) in TRAFFIC_THRESHOLDS.items():
        if low <= ratio < high:
            return level
    return "SEVERE"


def get_route_info(origin: str, destination: str) -> dict:
    """
    Geocode origin and destination via OpenStreetMap Nominatim,
    then calculate driving distance and duration via OSRM.

    Args:
        origin:      Origin address / city name
        destination: Destination address / city name

    Returns:
        {
            "distance_km": float,
            "base_duration_min": float,
            "traffic_duration_min": float,
            "traffic_level": str,
            "origin_address": str,
            "destination_address": str,
        }
    """
    logger.info("OSRM Routing for %s -> %s", origin, destination)

    # 1. Geocode origin
    r1 = requests.get(NOMINATIM_URL, params={"q": origin, "format": "json", "limit": 1}, headers=HEADERS, timeout=8)
    r1.raise_for_status()
    g1 = r1.json()
    if not g1:
        raise ValueError(f"Could not locate origin address: '{origin}'")

    lat1, lon1 = float(g1[0]["lat"]), float(g1[0]["lon"])
    origin_name = g1[0].get("display_name", origin)

    # 2. Geocode destination
    r2 = requests.get(NOMINATIM_URL, params={"q": destination, "format": "json", "limit": 1}, headers=HEADERS, timeout=8)
    r2.raise_for_status()
    g2 = r2.json()
    if not g2:
        raise ValueError(f"Could not locate destination address: '{destination}'")

    lat2, lon2 = float(g2[0]["lat"]), float(g2[0]["lon"])
    dest_name = g2[0].get("display_name", destination)

    # 3. OSRM driving route
    url = OSRM_ROUTE_URL.format(lon1=lon1, lat1=lat1, lon2=lon2, lat2=lat2)
    resp = requests.get(url, params={"overview": "false"}, headers=HEADERS, timeout=8)
    resp.raise_for_status()
    route_data = resp.json()

    if route_data.get("code") != "Ok" or not route_data.get("routes"):
        raise ValueError(f"OSRM Routing failed for coordinates: ({lat1},{lon1}) -> ({lat2},{lon2})")

    route = route_data["routes"][0]
    distance_m      = float(route["distance"])
    base_duration_s = float(route["duration"])

    # Traffic multiplier (1.25x average)
    traffic_mult       = 1.25
    traffic_duration_s = base_duration_s * traffic_mult

    distance_km = round(distance_m / 1000.0, 2)
    base_min    = round(base_duration_s / 60.0, 1)
    traffic_min = round(traffic_duration_s / 60.0, 1)
    traffic_lvl = _classify_traffic(base_duration_s, traffic_duration_s)

    return {
        "distance_km":          distance_km,
        "base_duration_min":    base_min,
        "traffic_duration_min":  traffic_min,
        "traffic_level":        traffic_lvl,
        "origin_address":       origin_name,
        "destination_address":  dest_name,
    }
