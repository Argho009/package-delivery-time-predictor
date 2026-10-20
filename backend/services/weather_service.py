"""
services/weather_service.py — OpenWeatherMap Current Weather API wrapper
Returns weather condition, temperature, wind speed, and precipitation.
Includes robust fallback if API key is missing, unauthorized (activating), or failing.
"""

import logging
from concurrent.futures import ThreadPoolExecutor
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from config import config

logger = logging.getLogger(__name__)

OWM_URL = "https://api.openweathermap.org/data/2.5/weather"

# Persistent HTTP session with connection pooling
_weather_session = requests.Session()
_retries = Retry(total=2, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
_adapter = HTTPAdapter(pool_connections=20, pool_maxsize=20, max_retries=_retries)
_weather_session.mount("https://", _adapter)
_weather_session.mount("http://", _adapter)

DEFAULT_WEATHER = {
    "weather_condition":   "CLEAR",
    "temperature_celsius": 25.0,
    "wind_speed_kmh":      10.0,
    "precipitation_mm":    0.0,
    "humidity_pct":        50,
    "description":         "clear sky (default)",
}


def _map_weather_condition(owm_id: int) -> str:
    if owm_id in range(200, 300):   return "STORM"
    if owm_id in range(300, 400):   return "RAIN"
    if owm_id in range(500, 505):
        return "HEAVY_RAIN" if owm_id >= 502 else "RAIN"
    if owm_id == 511:               return "SNOW"
    if owm_id in range(520, 532):   return "RAIN"
    if owm_id in range(600, 700):   return "SNOW"
    if owm_id in range(700, 800):   return "FOG"
    if owm_id == 800:               return "CLEAR"
    if owm_id in range(801, 805):   return "CLOUDY"
    return "CLOUDY"


_WEATHER_GRID_CACHE = {}


def get_weather_by_coords(lat: float, lon: float, location_name: str = "") -> dict:
    """
    Fetch current weather for specific coordinates from OpenWeatherMap.
    Uses geospatial grid caching (round to 1 decimal place = ~11 km) to avoid duplicate API calls.
    """
    grid_key = (round(lat, 1), round(lon, 1))
    if grid_key in _WEATHER_GRID_CACHE:
        cached = _WEATHER_GRID_CACHE[grid_key].copy()
        if location_name:
            cached["location_name"] = location_name
        cached["lat"] = lat
        cached["lon"] = lon
        return cached

    if not config.OPENWEATHER_API_KEY:
        res = DEFAULT_WEATHER.copy()
        res["location_name"] = location_name
        res["lat"] = lat
        res["lon"] = lon
        return res

    params = {
        "lat":   lat,
        "lon":   lon,
        "appid": config.OPENWEATHER_API_KEY,
        "units": "metric",
    }

    try:
        resp = _weather_session.get(OWM_URL, params=params, timeout=6)
        if resp.status_code == 401:
            logger.warning("OpenWeather key unauthorized (activating); using fallback weather.")
            res = DEFAULT_WEATHER.copy()
            res["location_name"] = location_name
            res["lat"] = lat
            res["lon"] = lon
            return res
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        logger.warning("OpenWeather API call failed (%s); using fallback weather.", e)
        res = DEFAULT_WEATHER.copy()
        res["location_name"] = location_name
        res["lat"] = lat
        res["lon"] = lon
        return res

    if data.get("cod") != 200:
        logger.warning("OpenWeather returned cod %s; using fallback weather.", data.get("cod"))
        res = DEFAULT_WEATHER.copy()
        res["location_name"] = location_name
        res["lat"] = lat
        res["lon"] = lon
        return res

    owm_id      = data["weather"][0]["id"]
    condition   = _map_weather_condition(owm_id)
    temp_c      = round(data["main"]["temp"], 1)
    wind_ms     = data["wind"].get("speed", 0)
    wind_kmh    = round(wind_ms * 3.6, 1)
    rain_1h     = data.get("rain", {}).get("1h", 0.0)
    snow_1h     = data.get("snow", {}).get("1h", 0.0)
    precip      = round(rain_1h + snow_1h, 1)
    humidity    = data["main"].get("humidity", 0)
    description = data["weather"][0].get("description", "")
    city_name   = data.get("name") or location_name

    weather_res = {
        "location_name":       city_name,
        "lat":                 lat,
        "lon":                 lon,
        "weather_condition":   condition,
        "temperature_celsius": temp_c,
        "wind_speed_kmh":      wind_kmh,
        "precipitation_mm":    precip,
        "humidity_pct":        humidity,
        "description":         description,
    }

    _WEATHER_GRID_CACHE[grid_key] = weather_res
    return weather_res


def get_route_weather(waypoints: dict) -> dict:
    """
    Fetch multi-point weather along the route: Origin, Midpoint, Destination in parallel.
    Returns individual checkpoint weather + aggregated route weather.
    """
    items = [
        ("origin", waypoints["origin"]["lat"], waypoints["origin"]["lon"], waypoints["origin"]["name"]),
        ("midpoint", waypoints["midpoint"]["lat"], waypoints["midpoint"]["lon"], waypoints["midpoint"]["name"]),
        ("destination", waypoints["destination"]["lat"], waypoints["destination"]["lon"], waypoints["destination"]["name"]),
    ]

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            key: executor.submit(get_weather_by_coords, lat, lon, name)
            for key, lat, lon, name in items
        }
        results = {key: fut.result() for key, fut in futures.items()}

    origin_w   = results["origin"]
    midpoint_w = results["midpoint"]
    dest_w     = results["destination"]

    # Determine most severe condition along the route
    severity_order = ["STORM", "HEAVY_RAIN", "SNOW", "RAIN", "FOG", "CLOUDY", "CLEAR"]
    all_conds = [origin_w["weather_condition"], midpoint_w["weather_condition"], dest_w["weather_condition"]]
    overall_cond = min(all_conds, key=lambda c: severity_order.index(c) if c in severity_order else 99)

    avg_temp = round((origin_w["temperature_celsius"] + midpoint_w["temperature_celsius"] + dest_w["temperature_celsius"]) / 3.0, 1)
    max_wind = max(origin_w["wind_speed_kmh"], midpoint_w["wind_speed_kmh"], dest_w["wind_speed_kmh"])
    total_precip = round(origin_w["precipitation_mm"] + midpoint_w["precipitation_mm"] + dest_w["precipitation_mm"], 1)

    return {
        "weather_condition":   overall_cond,
        "temperature_celsius": dest_w["temperature_celsius"], # destination temp for compatibility
        "avg_temperature_celsius": avg_temp,
        "wind_speed_kmh":      max_wind,
        "precipitation_mm":    total_precip,
        "humidity_pct":        dest_w["humidity_pct"],
        "description":         f"{origin_w['location_name']}: {origin_w['weather_condition']} -> Mid: {midpoint_w['weather_condition']} -> {dest_w['location_name']}: {dest_w['weather_condition']}",
        "checkpoints": {
            "origin":      origin_w,
            "midpoint":    midpoint_w,
            "destination": dest_w,
        }
    }


