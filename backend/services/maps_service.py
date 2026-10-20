import math
import logging
import random
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List, Dict
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

try:
    from services.indian_cities_geo import find_nearest_transit_city, get_adaptive_leg_step
except ImportError:
    from backend.services.indian_cities_geo import find_nearest_transit_city, get_adaptive_leg_step

logger = logging.getLogger(__name__)

NOMINATIM_URL  = "https://nominatim.openstreetmap.org/search"
OSRM_ROUTE_URL = "http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}"

HEADERS = {
    "User-Agent": "DeliverAI-Package-Delivery-Prediction-System/1.0"
}

# Persistent HTTP session with connection pooling
_session = requests.Session()
_retries = Retry(total=2, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
_adapter = HTTPAdapter(pool_connections=20, pool_maxsize=20, max_retries=_retries)
_session.mount("https://", _adapter)
_session.mount("http://", _adapter)
_session.headers.update(HEADERS)


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate Great Circle distance in km between two lat/lon points."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


@lru_cache(maxsize=512)
def geocode_location(query: str) -> dict:
    """
    Geocode address via OpenStreetMap Nominatim with in-memory LRU cache.
    Returns dict with lat, lon, display_name.
    """
    resp = _session.get(NOMINATIM_URL, params={"q": query.strip(), "format": "json", "limit": 1}, timeout=8)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise ValueError(f"Could not locate address: '{query}'")
    return {
        "lat": float(data[0]["lat"]),
        "lon": float(data[0]["lon"]),
        "display_name": data[0].get("display_name", query),
    }


def sample_route_waypoints(
    coords_latlon: list,
    total_distance_km: float,
    origin_name: str,
    dest_name: str,
    target_step_km: Optional[float] = None
) -> list:
    """
    Sample waypoints along the route polyline and resolve each checkpoint
    to actual Indian transit cities and logistics nodes.
    Returns list of checkpoint dicts with index, lat, lon, name, km_offset, is_major_marker.
    """
    orig_clean = origin_name.split(",")[0].strip()
    dest_clean = dest_name.split(",")[0].strip()

    if not coords_latlon or total_distance_km <= 15.0:
        return [
            {"index": 0, "lat": coords_latlon[0][0], "lon": coords_latlon[0][1], "name": orig_clean, "km_offset": 0.0, "is_major_marker": True},
            {"index": 1, "lat": coords_latlon[-1][0], "lon": coords_latlon[-1][1], "name": dest_clean, "km_offset": round(total_distance_km, 1), "is_major_marker": True}
        ]

    # Adaptive hop distance if not explicitly set
    effective_step = target_step_km if target_step_km and target_step_km > 0 else get_adaptive_leg_step(total_distance_km)
    num_segments = max(2, int(round(total_distance_km / effective_step)))
    actual_step = total_distance_km / num_segments

    # Cumulative distance along polyline points
    cum_dists = [0.0]
    curr = 0.0
    for i in range(1, len(coords_latlon)):
        d = haversine(coords_latlon[i-1][0], coords_latlon[i-1][1], coords_latlon[i][0], coords_latlon[i][1])
        curr += d
        cum_dists.append(curr)

    total_calc = cum_dists[-1] if cum_dists[-1] > 0 else 1.0

    sampled = [
        {"index": 0, "lat": coords_latlon[0][0], "lon": coords_latlon[0][1], "name": orig_clean, "km_offset": 0.0, "is_major_marker": True}
    ]

    seen_names = {orig_clean.lower(), dest_clean.lower()}
    last_major_km = 0.0
    major_interval = max(45.0, actual_step * 1.5)

    for seg in range(1, num_segments):
        target_km = seg * actual_step
        target_prop = (target_km / total_distance_km) * total_calc
        idx = next((i for i, d in enumerate(cum_dists) if d >= target_prop), len(cum_dists) - 1)
        lat, lon = coords_latlon[idx]

        # Resolve nearest transit city, excluding already visited checkpoints and destination
        resolved_city, dist_to_city = find_nearest_transit_city(
            lat, lon, max_distance_km=60.0, exclude_names=seen_names
        )

        if not resolved_city or resolved_city.lower() in seen_names:
            raw_city, _ = find_nearest_transit_city(lat, lon, max_distance_km=90.0)
            if raw_city and f"{raw_city} Bypass".lower() not in seen_names:
                resolved_city = f"{raw_city} Bypass"
            else:
                resolved_city = f"Corridor Hub ({round(target_km, 1)} km)"

        seen_names.add(resolved_city.lower())

        is_major = False
        if target_km - last_major_km >= major_interval:
            is_major = True
            last_major_km = target_km

        sampled.append({
            "index": seg,
            "lat": lat,
            "lon": lon,
            "name": resolved_city,
            "km_offset": round(target_km, 1),
            "is_major_marker": is_major,
        })

    sampled.append({
        "index": num_segments,
        "lat": coords_latlon[-1][0],
        "lon": coords_latlon[-1][1],
        "name": dest_clean,
        "km_offset": round(total_distance_km, 1),
        "is_major_marker": True,
    })

    return sampled



def get_route_info(origin: str, destination: str) -> dict:
    """
    Concurrently geocode origin and destination via OpenStreetMap Nominatim,
    then calculate driving distance and duration via OSRM.
    """
    logger.info("OSRM Routing for %s -> %s", origin, destination)

    # 1. Parallel Geocode origin and destination
    with ThreadPoolExecutor(max_workers=2) as executor:
        f_orig = executor.submit(geocode_location, origin)
        f_dest = executor.submit(geocode_location, destination)
        g1 = f_orig.result()
        g2 = f_dest.result()

    lat1, lon1 = g1["lat"], g1["lon"]
    origin_name = g1["display_name"]

    lat2, lon2 = g2["lat"], g2["lon"]
    dest_name = g2["display_name"]

    # 2. OSRM driving route with full geometry for waypoints
    url = OSRM_ROUTE_URL.format(lon1=lon1, lat1=lat1, lon2=lon2, lat2=lat2)
    resp = _session.get(url, params={"overview": "full", "geometries": "geojson"}, timeout=8)
    resp.raise_for_status()
    route_data = resp.json()

    if route_data.get("code") != "Ok" or not route_data.get("routes"):
        raise ValueError(f"OSRM Routing failed for coordinates: ({lat1},{lon1}) -> ({lat2},{lon2})")

    route = route_data["routes"][0]
    distance_m      = float(route["distance"])
    base_duration_s = float(route["duration"])

    # Geometry coordinates in [lat, lon] for Leaflet
    coords = route.get("geometry", {}).get("coordinates", [])
    polyline_coords = [[lat, lon] for [lon, lat] in coords] if coords else [[lat1, lon1], [lat2, lon2]]

    distance_km = round(distance_m / 1000.0, 2)
    base_min    = round(base_duration_s / 60.0, 1)

    # Traffic Engine Simulation
    traffic_multipliers = [("LOW", 1.05), ("MODERATE", 1.25), ("HIGH", 1.65), ("SEVERE", 2.10)]
    traffic_lvl, traffic_mult = random.choice(traffic_multipliers)
    
    traffic_duration_s = base_duration_s * traffic_mult
    traffic_min = round(traffic_duration_s / 60.0, 1)

    # Sample waypoints along polyline resolved to actual Indian cities
    sampled_waypoints = sample_route_waypoints(polyline_coords, distance_km, origin_name, dest_name)

    # Extract midpoint for fallback with resolved city name
    if coords:
        mid_idx = len(coords) // 2
        mid_lon, mid_lat = coords[mid_idx]
    else:
        mid_lat, mid_lon = (lat1 + lat2) / 2.0, (lon1 + lon2) / 2.0

    mid_city, _ = find_nearest_transit_city(mid_lat, mid_lon, max_distance_km=60.0)
    mid_name = f"Midpoint ({mid_city})" if mid_city else "Midpoint Route"

    waypoints = {
        "origin":      {"lat": lat1, "lon": lon1, "name": origin_name.split(",")[0].strip()},
        "midpoint":    {"lat": mid_lat, "lon": mid_lon, "name": mid_name},
        "destination": {"lat": lat2, "lon": lon2, "name": dest_name.split(",")[0].strip()},
    }

    return {
        "distance_km":          distance_km,
        "base_duration_min":    base_min,
        "traffic_duration_min":  traffic_min,
        "traffic_level":        traffic_lvl,
        "origin_address":       origin_name,
        "destination_address":  dest_name,
        "waypoints":            waypoints,
        "sampled_waypoints":    sampled_waypoints,
        "geometry":             polyline_coords,
    }
