"""
services/weather_service.py — OpenWeatherMap Current Weather API wrapper
Returns weather condition, temperature, wind speed, and precipitation.
Includes robust fallback if API key is missing, unauthorized (activating), or failing.
"""

import requests
import logging
from config import config

logger = logging.getLogger(__name__)

OWM_URL = "https://api.openweathermap.org/data/2.5/weather"

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


def get_weather(city: str) -> dict:
    """
    Fetch current weather for a city from OpenWeatherMap.
    Falls back gracefully to DEFAULT_WEATHER if API fails or key is activating.
    """
    if not config.OPENWEATHER_API_KEY:
        logger.warning("OPENWEATHER_API_KEY is missing; using default weather.")
        return DEFAULT_WEATHER

    params = {
        "q":     city,
        "appid": config.OPENWEATHER_API_KEY,
        "units": "metric",
    }

    try:
        resp = requests.get(OWM_URL, params=params, timeout=8)
        if resp.status_code == 401:
            logger.warning("OpenWeather key unauthorized (activating); using fallback weather.")
            return DEFAULT_WEATHER
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        logger.warning("OpenWeather API call failed (%s); using fallback weather.", e)
        return DEFAULT_WEATHER

    if data.get("cod") != 200:
        logger.warning("OpenWeather returned cod %s; using fallback weather.", data.get("cod"))
        return DEFAULT_WEATHER

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

    return {
        "weather_condition":   condition,
        "temperature_celsius": temp_c,
        "wind_speed_kmh":      wind_kmh,
        "precipitation_mm":    precip,
        "humidity_pct":        humidity,
        "description":         description,
    }
