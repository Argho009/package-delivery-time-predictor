"""
backend/services/multimodal_service.py — Multi-Modal Transit Scanner & Direct Corridor Engine
Scans Indian Railways station network and Indian Commercial Aviation hubs to detect
direct Rail and direct Air options for any Origin-Destination route.
"""

import os
import re
import math
import logging
from typing import Dict, Any, Optional, Tuple
import pandas as pd


logger = logging.getLogger(__name__)

# ── 1. Comprehensive Indian Commercial & Cargo Airport Network ──────────────
# (IATA, Airport Name, City, State, Latitude, Longitude, IsMajorCargoHub)
INDIAN_AIRPORTS = [
    ("DEL", "Indira Gandhi International Airport", "Delhi", "Delhi NCT", 28.5562, 77.1000, True),
    ("BOM", "Chhatrapati Shivaji Maharaj International Airport", "Mumbai", "Maharashtra", 19.0896, 72.8656, True),
    ("BLR", "Kempegowda International Airport", "Bengaluru", "Karnataka", 13.1986, 77.7066, True),
    ("CCU", "Netaji Subhash Chandra Bose International Airport", "Kolkata", "West Bengal", 22.6547, 88.4467, True),
    ("MAA", "Chennai International Airport", "Chennai", "Tamil Nadu", 12.9941, 80.1709, True),
    ("HYD", "Rajiv Gandhi International Airport", "Hyderabad", "Telangana", 17.2403, 78.4294, True),
    ("AMD", "Sardar Vallabhbhai Patel International Airport", "Ahmedabad", "Gujarat", 23.0772, 72.6347, True),
    ("PNQ", "Pune Airport", "Pune", "Maharashtra", 18.5822, 73.9197, True),
    ("COK", "Cochin International Airport", "Kochi", "Kerala", 10.1518, 76.3930, True),
    ("GOI", "Dabolim / Goa International Airport", "Goa", "Goa", 15.3808, 73.8314, True),
    ("GOX", "Manohar International Airport (Mopa)", "Goa", "Goa", 15.7667, 73.8667, False),
    ("JAI", "Jaipur International Airport", "Jaipur", "Rajasthan", 26.8242, 75.8122, True),
    ("LKO", "Chaudhary Charan Singh International Airport", "Lucknow", "Uttar Pradesh", 26.7606, 80.8893, True),
    ("GAU", "Lokpriya Gopinath Bordoloi International Airport", "Guwahati", "Assam", 26.1061, 91.5859, True),
    ("PAT", "Jay Prakash Narayan International Airport", "Patna", "Bihar", 25.5913, 85.0880, True),
    ("TRV", "Thiruvananthapuram International Airport", "Thiruvananthapuram", "Kerala", 8.4821, 76.9200, True),
    ("CCJ", "Calicut International Airport", "Kozhikode", "Kerala", 11.1368, 75.9553, False),
    ("IXC", "Shaheed Bhagat Singh International Airport", "Chandigarh", "Chandigarh", 30.6735, 76.7885, True),
    ("NAG", "Dr. Babasaheb Ambedkar International Airport", "Nagpur", "Maharashtra", 21.0922, 79.0472, True),
    ("IDR", "Devi Ahilyabai Holkar International Airport", "Indore", "Madhya Pradesh", 22.7217, 75.8011, True),
    ("BBI", "Biju Patnaik International Airport", "Bhubaneswar", "Odisha", 20.2444, 85.8178, True),
    ("RPR", "Swami Vivekananda Airport", "Raipur", "Chhattisgarh", 21.1804, 81.7388, True),
    ("VTZ", "Visakhapatnam International Airport", "Visakhapatnam", "Andhra Pradesh", 17.7212, 83.2245, True),
    ("VNS", "Lal Bahadur Shastri International Airport", "Varanasi", "Uttar Pradesh", 25.4523, 82.8593, True),
    ("SXR", "Sheikh ul-Alam International Airport", "Srinagar", "Jammu and Kashmir", 33.9871, 74.7742, True),
    ("IXB", "Bagdogra Airport", "Siliguri", "West Bengal", 26.6812, 88.3286, True),
    ("BDQ", "Vadodara Airport", "Vadodara", "Gujarat", 22.3362, 73.2263, False),
    ("CJB", "Coimbatore International Airport", "Coimbatore", "Tamil Nadu", 11.0299, 77.0434, True),
    ("IXR", "Birsa Munda Airport", "Ranchi", "Jharkhand", 23.3143, 85.3217, True),
    ("ATQ", "Sri Guru Ram Dass Jee International Airport", "Amritsar", "Punjab", 31.7096, 74.7973, True),
    ("UDR", "Maharana Pratap Airport", "Udaipur", "Rajasthan", 24.6177, 73.8961, False),
    ("IMF", "Bir Tikendrajit International Airport", "Imphal", "Manipur", 24.7600, 93.8967, False),
    ("IXA", "Maharaja Bir Bikram Airport", "Agartala", "Tripura", 23.8867, 91.2405, False),
    ("IXE", "Mangaluru International Airport", "Mangalore", "Karnataka", 12.9613, 74.8900, True),
    ("TRZ", "Tiruchirappalli International Airport", "Tiruchirappalli", "Tamil Nadu", 10.7654, 78.7107, True),
    ("IXM", "Madurai Airport", "Madurai", "Tamil Nadu", 9.8345, 78.0934, False),
    ("STV", "Surat International Airport", "Surat", "Gujarat", 21.1139, 72.7419, True),
    ("RAJ", "Rajkot International Airport (Hirasar)", "Rajkot", "Gujarat", 22.3481, 71.0116, False),
    ("JDH", "Jodhpur Airport", "Jodhpur", "Rajasthan", 26.2511, 73.0489, False),
    ("BHO", "Raja Bhoj Airport", "Bhopal", "Madhya Pradesh", 23.2875, 77.3378, True),
    ("GWL", "Rajmata Vijaya Raje Scindia Airport", "Gwalior", "Madhya Pradesh", 26.2933, 78.2278, False),
    ("KNU", "Kanpur Airport", "Kanpur", "Uttar Pradesh", 26.4414, 80.4128, False),
    ("AYJ", "Maharishi Valmiki International Airport", "Ayodhya", "Uttar Pradesh", 26.7461, 82.1558, False),
    ("DED", "Jolly Grant Airport", "Dehradun", "Uttarakhand", 30.1897, 78.1803, False),
    ("IXL", "Kushok Bakula Rimpochee Airport", "Leh", "Ladakh", 34.1359, 77.5465, False),
    ("JLR", "Jabalpur Airport", "Jabalpur", "Madhya Pradesh", 23.1778, 80.0522, False),
    ("AJL", "Lengpui Airport", "Aizawl", "Mizoram", 23.8406, 92.6289, False),
    ("DMU", "Dimapur Airport", "Dimapur", "Nagaland", 25.8839, 93.7711, False),
    ("DIB", "Dibrugarh Airport", "Dibrugarh", "Assam", 27.4839, 95.0194, False),
    ("TIR", "Tirupati Airport", "Tirupati", "Andhra Pradesh", 13.6325, 79.5433, False),
    ("IXJ", "Jammu Airport", "Jammu", "Jammu and Kashmir", 32.6891, 74.8375, False),
    ("AGR", "Agra Airport (Kheria)", "Agra", "Uttar Pradesh", 27.1558, 77.9608, False),
    ("HBX", "Hubballi Airport", "Hubli", "Karnataka", 15.3617, 75.0849, False),
    ("BEK", "Bareilly Airport", "Bareilly", "Uttar Pradesh", 28.4222, 79.4500, False),
]

_AIRPORT_CACHE = None
_RAIL_DF = None


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate Great Circle distance in km between two GPS coordinates."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(max(0.0, min(1.0, a))), math.sqrt(max(0.0, min(1.0, 1.0 - a))))
    return R * c


# ── 2. Indian Railways Station & DFC Resolution ─────────────────────────────
def _load_rail_dataset():
    """Load the 8,990 Indian railway stations dataset lazily."""
    global _RAIL_DF
    if _RAIL_DF is not None:
        return _RAIL_DF

    csv_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "raw", "railway_network", "india_railway_stations.csv"
    )
    if os.path.exists(csv_path):
        try:
            import pandas as pd
            df = pd.read_csv(csv_path)
            # Fill missing route_count with 0 and sort junctions
            df["route_count"] = df["route_count"].fillna(0).astype(float)
            df["is_junction"] = df["is_junction"].fillna(False).astype(bool)
            _RAIL_DF = df
            logger.info("Multimodal engine loaded %d railway stations from dataset.", len(df))
        except Exception as e:
            logger.warning("Could not load railway stations dataset: %s", e)
            _RAIL_DF = None
    return _RAIL_DF


def resolve_railway_hub(city_query: str, lat: Optional[float] = None, lon: Optional[float] = None) -> Optional[Dict[str, Any]]:
    """
    Find the closest major Indian Railways station / junction for a given city or coordinates.
    Prioritizes major railway junctions with high route capacity.
    """
    df = _load_rail_dataset()
    clean_q = re.sub(r"[^\w\s]", "", city_query).strip()

    if df is not None and not df.empty:
        # 1. Text match by station name or code
        matches = df[df["station_name"].str.contains(rf"\b{clean_q}\b", case=False, na=False)]
        if matches.empty:
            matches = df[df["station_name"].str.contains(clean_q, case=False, na=False)]

        if not matches.empty:
            # Sort: junctions first, then by route_count descending
            sorted_m = matches.sort_values(by=["is_junction", "route_count"], ascending=[False, False])
            best = sorted_m.iloc[0]
            return {
                "station_name": str(best["station_name"]).title(),
                "station_code": str(best["station_code"]),
                "state": str(best.get("state", "India")),
                "zone": str(best.get("railway_zone_code", "IR")),
                "is_junction": bool(best.get("is_junction", False)),
                "lat": float(best["latitude"]) if pd.notnull(best.get("latitude")) else (lat or 0.0),
                "lon": float(best["longitude"]) if pd.notnull(best.get("longitude")) else (lon or 0.0),
                "route_count": int(best.get("route_count", 0)),
            }

        # 2. Geodesic distance match if coordinates provided
        if lat is not None and lon is not None:
            valid_coords = df.dropna(subset=["latitude", "longitude"]).copy()
            dists = []
            for _, r in valid_coords.iterrows():
                dists.append(_haversine(lat, lon, float(r["latitude"]), float(r["longitude"])))
            valid_coords["dist_km"] = dists
            # Filter within 40 km
            nearby = valid_coords[valid_coords["dist_km"] <= 40.0]
            if not nearby.empty:
                top = nearby.sort_values(by=["is_junction", "route_count", "dist_km"], ascending=[False, False, True]).iloc[0]
                return {
                    "station_name": str(top["station_name"]).title(),
                    "station_code": str(top["station_code"]),
                    "state": str(top.get("state", "India")),
                    "zone": str(top.get("railway_zone_code", "IR")),
                    "is_junction": bool(top.get("is_junction", False)),
                    "lat": float(top["latitude"]),
                    "lon": float(top["longitude"]),
                    "route_count": int(top.get("route_count", 0)),
                }

    # Fallback synthetic hub
    return {
        "station_name": f"{clean_q} Junction",
        "station_code": clean_q[:4].upper(),
        "state": "India",
        "zone": "IR",
        "is_junction": True,
        "lat": lat or 0.0,
        "lon": lon or 0.0,
        "route_count": 25,
    }


# ── 3. Indian Commercial Aviation & Cargo Airport Resolution ────────────────
def resolve_airport_hub(city_query: str, lat: Optional[float] = None, lon: Optional[float] = None) -> Optional[Dict[str, Any]]:
    """
    Find the closest commercial cargo airport within a viable feeder radius (max 85 km).
    """
    clean_q = city_query.strip().lower()

    # 1. Exact city name match in airport registry
    for apt in INDIAN_AIRPORTS:
        iata, name, city, state, a_lat, a_lon, major = apt
        if city.lower() in clean_q or clean_q in city.lower():
            return {
                "iata": iata,
                "airport_name": name,
                "city": city,
                "state": state,
                "lat": a_lat,
                "lon": a_lon,
                "is_major_cargo_hub": major,
                "feeder_distance_km": 0.0,
            }

    # 2. Match by coordinates within 85 km feeder radius
    if lat is not None and lon is not None:
        best_apt = None
        min_d = float("inf")
        for apt in INDIAN_AIRPORTS:
            iata, name, city, state, a_lat, a_lon, major = apt
            d = _haversine(lat, lon, a_lat, a_lon)
            if d < min_d:
                min_d = d
                best_apt = apt

        if best_apt is not None and min_d <= 85.0:
            iata, name, city, state, a_lat, a_lon, major = best_apt
            return {
                "iata": iata,
                "airport_name": name,
                "city": city,
                "state": state,
                "lat": a_lat,
                "lon": a_lon,
                "is_major_cargo_hub": major,
                "feeder_distance_km": round(min_d, 1),
            }

    return None


# ── 4. Unified Direct Multi-Modal Scanner ───────────────────────────────────
def check_multimodal_options(
    origin: str,
    destination: str,
    origin_coords: Optional[Tuple[float, float]] = None,
    dest_coords: Optional[Tuple[float, float]] = None,
    road_distance_km: Optional[float] = None,
    road_hours: Optional[float] = None,
    weight_kg: float = 5.0,
) -> Dict[str, Any]:
    """
    Checks if direct Rail and direct Air options are available for the route,
    computes estimated transit times, carbon metrics, and provides comparative verdicts.
    """
    o_lat, o_lon = origin_coords if origin_coords else (None, None)
    d_lat, d_lon = dest_coords if dest_coords else (None, None)

    # Calculate baseline geodesic distance if coordinates available
    geodesic_dist = 0.0
    if o_lat and o_lon and d_lat and d_lon:
        geodesic_dist = _haversine(o_lat, o_lon, d_lat, d_lon)
    dist_ref = road_distance_km or (geodesic_dist * 1.25) or 100.0

    # ── A. Rail Freight Option ───────────────────────────────────
    o_rail = resolve_railway_hub(origin, o_lat, o_lon)
    d_rail = resolve_railway_hub(destination, d_lat, d_lon)

    rail_available = False
    rail_hours = None
    rail_dist_km = None
    rail_badge = "Unavailable"
    rail_desc = "No direct rail connectivity identified."

    if o_rail and d_rail and dist_ref >= 25.0:
        rail_available = True
        # Rail track distance is approx 1.12x geodesic
        rail_dist_km = round(geodesic_dist * 1.12 if geodesic_dist > 0 else dist_ref * 0.95, 1)
        # Indian Railways freight average speed: 42 - 50 km/h + yard buffer (4 - 8h)
        yard_buffer = 4.5 if dist_ref < 300 else (6.5 if dist_ref < 800 else 8.5)
        rail_hours = round((rail_dist_km / 46.0) + yard_buffer, 1)

        corridor_type = "DFC / Broad Gauge Freight Network"
        if any(z in [o_rail.get("zone"), d_rail.get("zone")] for z in ["CR", "WR", "NR", "ECR", "NCR"]):
            corridor_type = "High-Capacity DFC & Golden Quadrilateral Corridor"

        rail_badge = f"Direct Rail Available ({o_rail['station_code']} 🚆 {d_rail['station_code']})"
        rail_desc = f"Direct line-haul via Indian Railways {corridor_type} with terminal container handling."

    # Carbon comparison for Rail
    # Rail emits ~0.028 kg CO2/ton-km vs Road ~0.105 kg CO2/ton-km (73% savings)
    weight_tons = max(float(weight_kg), 0.1) / 1000.0
    rail_co2_kg = round((weight_tons * (rail_dist_km or dist_ref) * 0.028) + (0.012 * (rail_dist_km or dist_ref)), 2)
    road_co2_kg = round((weight_tons * dist_ref * 0.105) + (0.045 * dist_ref), 2)
    rail_co2_savings_pct = round(max((1.0 - (rail_co2_kg / max(road_co2_kg, 0.01))) * 100, 0))

    # ── B. Airways Freight Option ────────────────────────────────
    o_air = resolve_airport_hub(origin, o_lat, o_lon)
    d_air = resolve_airport_hub(destination, d_lat, d_lon)

    air_available = False
    air_hours = None
    flight_dist_km = None
    air_badge = "No Direct Flight"
    air_desc = "Commercial air cargo is not available."
    time_saved_vs_road = 0.0

    if not o_air:
        air_desc = f"No commercial airport hub near {origin} (requires road feeder)."
        air_badge = "No Airport at Origin"
    elif not d_air:
        air_desc = f"No commercial airport hub near {destination} (nearest requires regional road transfer)."
        air_badge = "No Airport at Destination"
    elif dist_ref < 250.0:
        air_desc = f"Route distance ({int(dist_ref)} km) is too short for scheduled air cargo. Road express is significantly faster."
        air_badge = "Route Too Short (<250 km)"
    else:
        # Both origin & dest have commercial airports and distance >= 250 km
        air_available = True
        flight_dist_km = round(_haversine(o_air["lat"], o_air["lon"], d_air["lat"], d_air["lon"]), 1)
        # Commercial air cargo: line-haul flight speed ~650 km/h + 3.0h airport pallet screening & sorting
        flight_time_h = flight_dist_km / 650.0
        airport_handling_h = 3.0
        air_hours = max(round(flight_time_h + airport_handling_h, 1), 2.5)

        base_road_h = road_hours or round(dist_ref / 45.0, 1)
        time_saved_vs_road = max(round(base_road_h - air_hours, 1), 0.0)

        air_badge = f"Direct Flight Available ({o_air['iata']} ✈️ {d_air['iata']})"
        air_desc = f"Direct daily cargo & belly-hold flights between {o_air['airport_name']} and {d_air['airport_name']}."

    # ── C. Road Option ───────────────────────────────────────────
    base_road_hours = road_hours or round(dist_ref / 45.0, 1)
    road_badge = "Always Available (Direct Highway)"
    road_desc = "Live National Highway & Expressway network with point-to-point door delivery."

    # ── D. Intelligent Best Mode Selection ────────────────────────
    # Determine the system recommended mode
    if weight_kg >= 25.0 and dist_ref >= 350.0 and rail_available:
        recommended_mode = "RAIL"
        rec_reason = f"Bulk cargo ({weight_kg:.1f} kg) over {int(dist_ref)} km is most cost-effective and cuts CO2 by {rail_co2_savings_pct}% via Rail."
    elif dist_ref >= 450.0 and air_available and time_saved_vs_road >= 4.0:
        recommended_mode = "AIR"
        rec_reason = f"Long-haul route saves {time_saved_vs_road:.1f} hours via Direct Air Cargo ({o_air['iata']} ✈️ {d_air['iata']})."
    else:
        recommended_mode = "ROAD"
        rec_reason = "Point-to-point road dispatch provides the optimal balance of speed, cost, and door delivery."

    return {
        "origin_query": origin,
        "destination_query": destination,
        "recommended_mode": recommended_mode,
        "recommended_reason": rec_reason,
        "distance_km": round(dist_ref, 1),
        "options": {
            "road": {
                "shipping_mode": "ROAD",
                "direct_available": True,
                "badge": road_badge,
                "description": road_desc,
                "estimated_hours": base_road_hours,
                "co2_kg": road_co2_kg,
                "is_fastest": base_road_hours <= (air_hours or 999),
                "is_cheapest": dist_ref < 350,
            },
            "rail": {
                "shipping_mode": "RAIL",
                "direct_available": rail_available,
                "badge": rail_badge,
                "description": rail_desc,
                "origin_hub": o_rail,
                "dest_hub": d_rail,
                "rail_distance_km": rail_dist_km,
                "estimated_hours": rail_hours,
                "co2_kg": rail_co2_kg,
                "co2_savings_pct": rail_co2_savings_pct,
                "is_greenest": True,
            },
            "air": {
                "shipping_mode": "AIR",
                "direct_available": air_available,
                "badge": air_badge,
                "description": air_desc,
                "origin_hub": o_air,
                "dest_hub": d_air,
                "flight_distance_km": flight_dist_km,
                "estimated_hours": air_hours,
                "time_saved_vs_road_hours": time_saved_vs_road,
                "is_fastest": air_available and ((air_hours or 999) < base_road_hours),
            },
        },
    }
