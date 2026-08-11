import math
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


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate Great Circle distance in km between two lat/lon points."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def sample_route_waypoints(coords_latlon: list, total_distance_km: float, origin_name: str, dest_name: str, target_step_km: float = 10.0) -> list:
    """
    Sample waypoints every ~10 km along the polyline coordinates.
    Returns list of checkpoint dicts with index, lat, lon, name, km_offset.
    """
    orig_clean = origin_name.split(",")[0].strip()
    dest_clean = dest_name.split(",")[0].strip()

    if not coords_latlon or total_distance_km <= 15.0:
        return [
            {"index": 0, "lat": coords_latlon[0][0], "lon": coords_latlon[0][1], "name": orig_clean, "km_offset": 0.0, "is_major_marker": True},
            {"index": 1, "lat": coords_latlon[-1][0], "lon": coords_latlon[-1][1], "name": dest_clean, "km_offset": round(total_distance_km, 1), "is_major_marker": True}
        ]

    num_segments = max(2, int(round(total_distance_km / target_step_km)))
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

    last_major_km = 0.0
    for seg in range(1, num_segments):
        target_km = seg * actual_step
        target_prop = (target_km / total_distance_km) * total_calc
        idx = next((i for i, d in enumerate(cum_dists) if d >= target_prop), len(cum_dists) - 1)
        lat, lon = coords_latlon[idx]

        # Major marker every ~50 km
        is_major = False
        if target_km - last_major_km >= 45.0:
            is_major = True
            last_major_km = target_km

        sampled.append({
            "index": seg,
            "lat": lat,
            "lon": lon,
            "name": f"Leg {seg} ({round(target_km, 1)} km)",
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

    # 3. OSRM driving route with full geometry for waypoints
    url = OSRM_ROUTE_URL.format(lon1=lon1, lat1=lat1, lon2=lon2, lat2=lat2)
    resp = requests.get(url, params={"overview": "full", "geometries": "geojson"}, headers=HEADERS, timeout=8)
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

    # Traffic multiplier (1.25x average)
    traffic_mult       = 1.25
    traffic_duration_s = base_duration_s * traffic_mult
    traffic_min = round(traffic_duration_s / 60.0, 1)
    traffic_lvl = _classify_traffic(base_duration_s, traffic_duration_s)

    # Sample waypoints every ~10 km along polyline
    sampled_waypoints = sample_route_waypoints(polyline_coords, distance_km, origin_name, dest_name, target_step_km=10.0)

    # Extract midpoint for fallback
    if coords:
        mid_idx = len(coords) // 2
        mid_lon, mid_lat = coords[mid_idx]
    else:
        mid_lat, mid_lon = (lat1 + lat2) / 2.0, (lon1 + lon2) / 2.0

    waypoints = {
        "origin":      {"lat": lat1, "lon": lon1, "name": origin_name.split(",")[0].strip()},
        "midpoint":    {"lat": mid_lat, "lon": mid_lon, "name": "Midpoint Route"},
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
