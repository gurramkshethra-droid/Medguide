"""
MediGuide AI - Doctor and Clinic Finder Service
Powered by OpenStreetMap (Nominatim Geocoding and Overpass API).
Attribution: © OpenStreetMap contributors (ODbL License).
"""

import requests
import urllib.parse
import logging
import math

logger = logging.getLogger(__name__)

USER_AGENT = "MediGuideAI-HealthcarePlatform/1.0 (Academic PBL; https://mediguide.ai)"

# Fallback cache of verified real healthcare facilities for offline/test reliability
FALLBACK_CLINICS = {
    "hyderabad": [
        {
            "name": "Apollo Hospitals, Jubilee Hills",
            "type": "hospital",
            "specialty": "Multi-specialty / Cardiology / Emergency",
            "address": "Road No 72, Film Nagar, Jubilee Hills, Hyderabad, Telangana 500033",
            "phone": "+91 40 2360 7777",
            "opening_hours": "24/7 (Emergency & Inpatient)",
            "lat": 17.4262,
            "lon": 78.4116
        },
        {
            "name": "Yashoda Hospitals, Somajiguda",
            "type": "hospital",
            "specialty": "Multi-specialty / Pulmonology / Oncology",
            "address": "Raj Bhavan Rd, Somajiguda, Hyderabad, Telangana 500082",
            "phone": "+91 40 4567 4567",
            "opening_hours": "24/7",
            "lat": 17.4246,
            "lon": 78.4578
        },
        {
            "name": "Nizam's Institute of Medical Sciences (NIMS)",
            "type": "hospital",
            "specialty": "Neurology / Nephrology / Rheumatology",
            "address": "Punjagutta, Hyderabad, Telangana 500082",
            "phone": "+91 40 2348 9000",
            "opening_hours": "OPD: Mon-Sat 08:00-14:00; Emergency: 24/7",
            "lat": 17.4225,
            "lon": 78.4503
        }
    ],
    "bangalore": [
        {
            "name": "Manipal Hospital, Old Airport Road",
            "type": "hospital",
            "specialty": "Multi-specialty / Cardiology / Pediatrics",
            "address": "98, HAL Old Airport Rd, Kodihalli, Bengaluru, Karnataka 560017",
            "phone": "+91 80 2502 4444",
            "opening_hours": "24/7",
            "lat": 12.9592,
            "lon": 77.6499
        },
        {
            "name": "Fortis Hospital, Bannerghatta",
            "type": "hospital",
            "specialty": "Orthopedics / Gastroenterology / Surgery",
            "address": "154/9, Bannerghatta Main Rd, Bengaluru, Karnataka 560076",
            "phone": "+91 80 6621 4444",
            "opening_hours": "24/7",
            "lat": 12.8938,
            "lon": 77.5975
        }
    ],
    "new york": [
        {
            "name": "NewYork-Presbyterian / Weill Cornell Medical Center",
            "type": "hospital",
            "specialty": "Multi-specialty / Cardiology / Emergency",
            "address": "525 E 68th St, New York, NY 10065",
            "phone": "+1 212-746-5454",
            "opening_hours": "24/7",
            "lat": 40.7651,
            "lon": -73.9542
        },
        {
            "name": "Mount Sinai Hospital",
            "type": "hospital",
            "specialty": "Internal Medicine / Dermatology / Oncology",
            "address": "1468 Madison Ave, New York, NY 10029",
            "phone": "+1 212-241-6500",
            "opening_hours": "24/7",
            "lat": 40.7900,
            "lon": -73.9527
        }
    ],
    "london": [
        {
            "name": "St Thomas' Hospital (NHS)",
            "type": "hospital",
            "specialty": "General Medicine / Emergency / Cardiology",
            "address": "Westminster Bridge Rd, London SE1 7EH",
            "phone": "+44 20 7188 7188",
            "opening_hours": "24/7 A&E",
            "lat": 51.4988,
            "lon": -0.1187
        },
        {
            "name": "University College Hospital (UCLH)",
            "type": "hospital",
            "specialty": "Infectious Disease / Neurology / Surgery",
            "address": "235 Euston Rd, London NW1 2BU",
            "phone": "+44 20 3456 7890",
            "opening_hours": "24/7",
            "lat": 51.5255,
            "lon": -0.1368
        }
    ]
}


class DoctorFinderService:
    @staticmethod
    def geocode_location(location_query):
        """Geocode a city, area, or postal code using Nominatim."""
        if not location_query or not location_query.strip():
            return None

        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": location_query.strip(),
            "format": "json",
            "limit": 1
        }
        headers = {"User-Agent": USER_AGENT}

        try:
            resp = requests.get(url, params=params, headers=headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data and len(data) > 0:
                    return {
                        "lat": float(data[0]["lat"]),
                        "lon": float(data[0]["lon"]),
                        "display_name": data[0]["display_name"]
                    }
        except Exception as e:
            logger.warning(f"Nominatim geocoding failed or timed out: {e}")
        
        return None

    @staticmethod
    def search_overpass(lat, lon, radius_meters=6000, specialty_filter=None):
        """Query Overpass API for real hospitals, clinics, and doctors around coordinate."""
        overpass_url = "https://overpass-api.de/api/interpreter"
        query = f"""
        [out:json][timeout:8];
        (
          node["amenity"~"hospital|clinic|doctors"](around:{radius_meters},{lat},{lon});
          way["amenity"~"hospital|clinic|doctors"](around:{radius_meters},{lat},{lon});
        );
        out center 25;
        """
        headers = {"User-Agent": USER_AGENT}

        try:
            resp = requests.post(overpass_url, data={"data": query}, headers=headers, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                elements = data.get("elements", [])
                results = []

                for el in elements:
                    tags = el.get("tags", {})
                    name = tags.get("name")
                    if not name:
                        continue  # Skip unnamed nodes to prevent showing blank cards

                    facility_lat = el.get("lat") or el.get("center", {}).get("lat")
                    facility_lon = el.get("lon") or el.get("center", {}).get("lon")
                    if not facility_lat or not facility_lon:
                        continue

                    # Extract address parts
                    addr_parts = [
                        tags.get("addr:housenumber", ""),
                        tags.get("addr:street", ""),
                        tags.get("addr:suburb", ""),
                        tags.get("addr:city", tags.get("addr:town", ""))
                    ]
                    address = ", ".join([p for p in addr_parts if p]) or tags.get("address", "Address details not published")

                    # Extract metadata without inventing
                    specialty = tags.get("healthcare:speciality") or tags.get("speciality") or tags.get("amenity", "Healthcare Clinic").capitalize()
                    phone = tags.get("phone") or tags.get("contact:phone") or None
                    opening_hours = tags.get("opening_hours") or None
                    website = tags.get("website") or tags.get("contact:website") or None

                    results.append({
                        "name": name,
                        "type": tags.get("amenity", "clinic"),
                        "specialty": specialty,
                        "address": address,
                        "phone": phone,
                        "opening_hours": opening_hours,
                        "website": website,
                        "lat": facility_lat,
                        "lon": facility_lon,
                        "directions_url": f"https://www.openstreetmap.org/directions?engine=fossgis_osrm_car&route={lat},{lon};{facility_lat},{facility_lon}"
                    })

                # Filter by specialty if requested
                if specialty_filter and specialty_filter.strip():
                    sf = specialty_filter.lower().strip()
                    filtered = [
                        r for r in results
                        if sf in r["specialty"].lower() or sf in r["name"].lower()
                    ]
                    return filtered if filtered else results
                
                return results

        except Exception as e:
            logger.warning(f"Overpass API request failed or timed out: {e}")

        return None

    @staticmethod
    def find_doctors(location_text=None, lat=None, lon=None, specialty=None):
        """Unified discovery function combining geocoding, Overpass, and verified fallbacks."""
        center_name = None

        if lat is not None and lon is not None:
            center_name = f"Your Location ({lat:.4f}, {lon:.4f})"
        elif location_text and location_text.strip():
            geo = DoctorFinderService.geocode_location(location_text)
            if geo:
                lat = geo["lat"]
                lon = geo["lon"]
                center_name = geo["display_name"]
            else:
                # Check if we have offline fallback matching the city keyword
                loc_lower = location_text.lower().strip()
                for city, clinics in FALLBACK_CLINICS.items():
                    if city in loc_lower:
                        return {
                            "status": "success",
                            "source": "Verified Healthcare Directory (Offline/Cached)",
                            "location_name": city.title(),
                            "results": clinics,
                            "attribution": "Data curated from verified hospital directories & OpenStreetMap"
                        }
                return {
                    "status": "error",
                    "error": f"Could not find coordinates for '{location_text}'. Please try a larger nearby city or postal code."
                }
        else:
            return {
                "status": "error",
                "error": "Please provide a location name, postal code, or share your GPS coordinates."
            }

        # Query live Overpass API
        live_results = DoctorFinderService.search_overpass(lat, lon, specialty_filter=specialty)
        if live_results is not None and len(live_results) > 0:
            return {
                "status": "success",
                "source": "OpenStreetMap Live Overpass API",
                "location_name": center_name,
                "results": live_results,
                "attribution": "© OpenStreetMap contributors (ODbL License)"
            }

        # Check offline cache if live returned empty or timed out
        if location_text:
            loc_lower = location_text.lower()
            for city, clinics in FALLBACK_CLINICS.items():
                if city in loc_lower:
                    return {
                        "status": "success",
                        "source": "Verified Healthcare Directory (Fallback)",
                        "location_name": city.title(),
                        "results": clinics,
                        "attribution": "Data curated from verified regional hospital directories & OpenStreetMap"
                    }

        if live_results is not None and len(live_results) == 0:
            return {
                "status": "empty",
                "location_name": center_name,
                "results": [],
                "message": "No healthcare clinics or hospitals were found within a 6km radius in OpenStreetMap."
            }

        return {
            "status": "service_unavailable",
            "location_name": center_name,
            "results": [],
            "message": "The OpenStreetMap public Overpass service is currently busy or unreachable. Please try again shortly or search a major metropolitan center."
        }

doctor_service = DoctorFinderService()
