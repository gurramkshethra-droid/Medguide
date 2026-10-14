"""
Nearby care finder using OpenStreetMap only.

- Nominatim geocoding (identifying User-Agent, ~1 request/second)
- Overpass amenity=hospital|clinic|doctors within 5 km, out center
- No hardcoded hospital lists, no fabricated fields
Attribution: Map data (c) OpenStreetMap contributors
"""

from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, timezone

import requests

logger = logging.getLogger(__name__)

USER_AGENT = "MediGuideAI-StudentPBL/1.0 (academic project; contact: mediguide-pbl@localhost)"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
RADIUS_METERS = 5000
CACHE_SECONDS = 180
NOMINATIM_MIN_INTERVAL = 1.05
NOT_LISTED = "Not listed"


class DoctorFinderService:
    def __init__(self):
        self._cache = {}
        self._lock = threading.Lock()
        self._last_nominatim = 0.0

    def _cache_get(self, key):
        with self._lock:
            item = self._cache.get(key)
            if not item:
                return None
            if time.time() - item["ts"] > CACHE_SECONDS:
                self._cache.pop(key, None)
                return None
            return item["value"]

    def _cache_set(self, key, value):
        with self._lock:
            self._cache[key] = {"ts": time.time(), "value": value}

    def _throttle_nominatim(self):
        with self._lock:
            wait = NOMINATIM_MIN_INTERVAL - (time.time() - self._last_nominatim)
            if wait > 0:
                time.sleep(wait)
            self._last_nominatim = time.time()

    @staticmethod
    def _present_or_not_listed(value):
        if value is None:
            return NOT_LISTED
        text = str(value).strip()
        return text if text else NOT_LISTED

    def geocode_location(self, location_query):
        if not location_query or not str(location_query).strip():
            return {"status": "error", "error": "Please enter a city, area, or postal code."}

        query = str(location_query).strip()
        cache_key = f"geo:{query.lower()}"
        cached = self._cache_get(cache_key)
        if cached is not None:
            return cached

        self._throttle_nominatim()
        try:
            resp = requests.get(
                NOMINATIM_URL,
                params={"q": query, "format": "json", "limit": 1},
                headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
                timeout=8,
            )
        except requests.Timeout:
            return {"status": "timeout", "error": "Location lookup timed out. Please try again."}
        except requests.RequestException as exc:
            logger.warning("Nominatim request failed: %s", exc)
            return {"status": "error", "error": "Location lookup is currently unavailable."}

        if resp.status_code == 429:
            result = {
                "status": "rate_limited",
                "error": "The geocoding service asked us to slow down. Wait a few seconds and try again.",
            }
            return result
        if resp.status_code != 200:
            return {"status": "error", "error": "Location lookup is currently unavailable."}

        data = resp.json() if resp.content else []
        if not data:
            result = {
                "status": "not_found",
                "error": f"Location not found for '{query}'. Try a larger nearby city or postal code.",
            }
            self._cache_set(cache_key, result)
            return result

        result = {
            "status": "ok",
            "lat": float(data[0]["lat"]),
            "lon": float(data[0]["lon"]),
            "display_name": data[0].get("display_name") or query,
        }
        self._cache_set(cache_key, result)
        return result

    def search_overpass(self, lat, lon, specialty_filter=None):
        query = f"""
        [out:json][timeout:12];
        (
          node["amenity"~"hospital|clinic|doctors"](around:{RADIUS_METERS},{lat},{lon});
          way["amenity"~"hospital|clinic|doctors"](around:{RADIUS_METERS},{lat},{lon});
          relation["amenity"~"hospital|clinic|doctors"](around:{RADIUS_METERS},{lat},{lon});
        );
        out center 40;
        """
        try:
            resp = requests.post(
                OVERPASS_URL,
                data={"data": query},
                headers={"User-Agent": USER_AGENT},
                timeout=15,
            )
        except requests.Timeout:
            return {"status": "timeout", "error": "The map service timed out. Please try again shortly."}
        except requests.RequestException as exc:
            logger.warning("Overpass request failed: %s", exc)
            return {"status": "error", "error": "The map service is currently unavailable."}

        if resp.status_code == 429:
            return {
                "status": "rate_limited",
                "error": "The map service asked us to slow down. Wait a few seconds and try again.",
            }
        if resp.status_code != 200:
            return {"status": "error", "error": "The map service is currently unavailable."}

        payload = resp.json() if resp.content else {}
        elements = payload.get("elements") or []
        results = []
        for el in elements:
            tags = el.get("tags") or {}
            name = (tags.get("name") or "").strip()
            if not name:
                continue
            facility_lat = el.get("lat") or (el.get("center") or {}).get("lat")
            facility_lon = el.get("lon") or (el.get("center") or {}).get("lon")
            addr_parts = [
                tags.get("addr:housenumber", ""),
                tags.get("addr:street", ""),
                tags.get("addr:suburb", ""),
                tags.get("addr:city") or tags.get("addr:town") or tags.get("addr:place", ""),
            ]
            address_joined = ", ".join(p for p in addr_parts if p)
            phone = tags.get("phone") or tags.get("contact:phone")
            hours = tags.get("opening_hours")
            website = tags.get("website") or tags.get("contact:website")
            amenity = tags.get("amenity")
            specialty = tags.get("healthcare:speciality") or tags.get("speciality")

            directions = None
            if facility_lat is not None and facility_lon is not None:
                directions = (
                    "https://www.google.com/maps/dir/?api=1&destination="
                    f"{facility_lat},{facility_lon}"
                )

            results.append(
                {
                    "name": name,
                    "type": self._present_or_not_listed(amenity),
                    "address": self._present_or_not_listed(address_joined),
                    "phone": self._present_or_not_listed(phone),
                    "opening_hours": self._present_or_not_listed(hours),
                    "website": self._present_or_not_listed(website),
                    "specialty": self._present_or_not_listed(specialty),
                    "lat": facility_lat,
                    "lon": facility_lon,
                    "directions_url": directions,
                }
            )

        if specialty_filter and str(specialty_filter).strip():
            needle = specialty_filter.lower().strip()
            filtered = [
                row
                for row in results
                if needle in str(row.get("specialty", "")).lower()
                or needle in str(row.get("name", "")).lower()
                or needle in str(row.get("type", "")).lower()
            ]
            results = filtered

        return {"status": "ok", "results": results}

    def find_doctors(self, location_text=None, lat=None, lon=None, specialty=None):
        attribution = "Map data (c) OpenStreetMap contributors"
        center_name = None

        if lat is not None and lon is not None:
            try:
                lat = float(lat)
                lon = float(lon)
            except (TypeError, ValueError):
                return {
                    "status": "error",
                    "error": "The provided coordinates were not valid.",
                    "results": [],
                    "attribution": attribution,
                }
            center_name = f"Selected location ({lat:.4f}, {lon:.4f})"
        else:
            if not location_text or not str(location_text).strip():
                return {
                    "status": "error",
                    "error": "Please enter a city, area, or postal code, or use your location.",
                    "results": [],
                    "attribution": attribution,
                }
            geo = self.geocode_location(location_text)
            if geo.get("status") != "ok":
                return {
                    "status": geo.get("status", "error"),
                    "error": geo.get("error", "Location lookup failed."),
                    "results": [],
                    "attribution": attribution,
                }
            lat = geo["lat"]
            lon = geo["lon"]
            center_name = geo["display_name"]

        cache_key = f"ov:{round(lat, 4)}:{round(lon, 4)}:{(specialty or '').lower()}"
        cached = self._cache_get(cache_key)
        if cached is not None:
            payload = dict(cached)
            payload["cached"] = True
            payload["attribution"] = attribution
            return payload

        overpass = self.search_overpass(lat, lon, specialty_filter=specialty)
        if overpass.get("status") != "ok":
            return {
                "status": overpass.get("status", "error"),
                "error": overpass.get("error", "Search failed."),
                "location_name": center_name,
                "results": [],
                "attribution": attribution,
            }

        results = overpass.get("results") or []
        if not results:
            payload = {
                "status": "empty",
                "location_name": center_name,
                "results": [],
                "message": "No hospitals, clinics, or doctors were listed within 5 km in OpenStreetMap.",
                "attribution": attribution,
                "queried_at": datetime.now(timezone.utc).isoformat(),
            }
            self._cache_set(cache_key, payload)
            return payload

        payload = {
            "status": "success",
            "source": "OpenStreetMap (Nominatim + Overpass)",
            "location_name": center_name,
            "results": results,
            "attribution": attribution,
            "queried_at": datetime.now(timezone.utc).isoformat(),
        }
        self._cache_set(cache_key, payload)
        return payload


doctor_service = DoctorFinderService()
