"""Small, bounded HTTP helpers for public travel APIs."""
from datetime import date
from decimal import Decimal
from threading import Lock
import time
from django.core.cache import cache
import requests
TIMEOUT = 7
HEADERS = {"User-Agent": "TripMate/1.0 (simple trip planner)"}
_geocode_lock = Lock()
_last_geocode_request = 0.0
def _get(url, **kwargs):
    response = requests.get(url, timeout=TIMEOUT, headers=HEADERS, **kwargs)
    response.raise_for_status()
    return response.json()
def geocode(place):
    global _last_geocode_request
    cache_key = f"tripmate-geocode:{place.strip().casefold()}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    try:
        with _geocode_lock:
            wait = 1.05 - (time.monotonic() - _last_geocode_request)
            if wait > 0:
                time.sleep(wait)
            _last_geocode_request = time.monotonic()
            rows = _get("https://nominatim.openstreetmap.org/search", params={"q": place, "format": "jsonv2", "limit": 1})
        point = (float(rows[0]["lat"]), float(rows[0]["lon"])) if rows else None
        if point:
            cache.set(cache_key, point, 60 * 60 * 24 * 30)
        return point
    except (requests.RequestException, ValueError, KeyError, IndexError, TypeError):
        return None
def weather(destination, coords=None):
    coords = coords or geocode(destination)
    if not coords: return None
    try:
        data = _get("https://api.open-meteo.com/v1/forecast", params={"latitude": coords[0], "longitude": coords[1], "current": "temperature_2m,apparent_temperature,weather_code", "daily": "temperature_2m_max,temperature_2m_min", "timezone": "auto"})
        return {"temperature": data["current"]["temperature_2m"], "feels_like": data["current"]["apparent_temperature"], "high": data["daily"]["temperature_2m_max"][0], "low": data["daily"]["temperature_2m_min"][0]}
    except (requests.RequestException, ValueError, KeyError, IndexError, TypeError): return None
def route(origin, destination, origin_coords=None, destination_coords=None):
    a, b = origin_coords or geocode(origin), destination_coords or geocode(destination)
    if not a or not b: return None
    try:
        data = _get(f"https://router.project-osrm.org/route/v1/driving/{a[1]},{a[0]};{b[1]},{b[0]}", params={"overview": "false"})
        result = data["routes"][0]
        return {"km": round(result["distance"] / 1000), "hours": round(result["duration"] / 3600, 1)}
    except (requests.RequestException, ValueError, KeyError, IndexError, TypeError): return None

def exchange(amount, source, target):
    if source == target: return amount
    try:
        data = _get("https://api.frankfurter.app/latest", params={"amount": str(amount), "from": source, "to": target})
        return Decimal(str(data["rates"][target]))
    except (requests.RequestException, ValueError, KeyError, TypeError): return None
def holidays(country, start, end):
    if not country or not start or not end: return None
    try:
        found = {}
        for year in range(start.year, end.year + 1):
            rows = _get(f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country}")
            for item in rows:
                day = date.fromisoformat(item["date"])
                if start <= day <= end: found[day] = item.get("localName") or item.get("name")
        return [{"date": day, "name": name} for day, name in sorted(found.items())]
    except (requests.RequestException, ValueError, KeyError, TypeError): return None
