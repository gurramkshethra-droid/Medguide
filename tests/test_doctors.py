import json

from services.doctor_service import DoctorFinderService, NOT_LISTED


HYDERABAD_GEO = [{
    "lat": "17.3850",
    "lon": "78.4867",
    "display_name": "Hyderabad, Telangana, India",
}]
LONDON_GEO = [{
    "lat": "51.5074",
    "lon": "-0.1278",
    "display_name": "London, England, United Kingdom",
}]
HYDERABAD_OVERPASS = {
    "elements": [
        {
            "type": "node",
            "lat": 17.412,
            "lon": 78.448,
            "tags": {
                "name": "Osmania General Hospital",
                "amenity": "hospital",
                "addr:city": "Hyderabad",
                "phone": "+91 40 2460 0101",
            },
        }
    ]
}
LONDON_OVERPASS = {
    "elements": [
        {
            "type": "node",
            "lat": 51.498,
            "lon": -0.118,
            "tags": {
                "name": "Guy's Hospital",
                "amenity": "hospital",
                "addr:city": "London",
                "website": "https://www.guysandstthomas.nhs.uk/",
            },
        }
    ]
}


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.content = b"{}" if payload is not None else b""

    def json(self):
        return self._payload


def test_empty_location_error():
    service = DoctorFinderService()
    result = service.find_doctors(location_text="  ")
    assert result["status"] == "error"
    assert result["results"] == []


def test_two_cities_return_different_results(monkeypatch):
    service = DoctorFinderService()

    def fake_get(url, params=None, headers=None, timeout=None):
        q = (params or {}).get("q", "").lower()
        if "hyderabad" in q:
            return FakeResponse(HYDERABAD_GEO)
        if "london" in q:
            return FakeResponse(LONDON_GEO)
        return FakeResponse([], 200)

    def fake_post(url, data=None, headers=None, timeout=None):
        body = (data or {}).get("data", "")
        if "17.385" in body:
            return FakeResponse(HYDERABAD_OVERPASS)
        if "51.5074" in body:
            return FakeResponse(LONDON_OVERPASS)
        return FakeResponse({"elements": []})

    monkeypatch.setattr("services.doctor_service.requests.get", fake_get)
    monkeypatch.setattr("services.doctor_service.requests.post", fake_post)

    hyd = service.find_doctors(location_text="Hyderabad")
    lon = service.find_doctors(location_text="London")
    assert hyd["status"] == "success"
    assert lon["status"] == "success"
    assert hyd["results"][0]["name"] == "Osmania General Hospital"
    assert lon["results"][0]["name"] == "Guy's Hospital"
    assert hyd["results"][0]["name"] != lon["results"][0]["name"]
    assert hyd["results"][0]["phone"] == "+91 40 2460 0101"
    assert lon["results"][0]["phone"] == NOT_LISTED
    assert hyd["results"][0]["website"] == NOT_LISTED
    assert "guysandstthomas" in lon["results"][0]["website"]
    assert "OpenStreetMap" in hyd["attribution"]


def test_location_not_found(monkeypatch):
    service = DoctorFinderService()
    monkeypatch.setattr(
        "services.doctor_service.requests.get",
        lambda *args, **kwargs: FakeResponse([], 200),
    )
    result = service.find_doctors(location_text="NotARealPlaceXYZ")
    assert result["status"] == "not_found"


def test_overpass_timeout(monkeypatch):
    import requests as req_mod

    service = DoctorFinderService()
    monkeypatch.setattr(
        "services.doctor_service.requests.get",
        lambda *args, **kwargs: FakeResponse(HYDERABAD_GEO),
    )

    def boom(*args, **kwargs):
        raise req_mod.Timeout("overpass timeout")

    monkeypatch.setattr("services.doctor_service.requests.post", boom)
    result = service.find_doctors(location_text="Hyderabad")
    assert result["status"] == "timeout"


def test_rate_limit(monkeypatch):
    service = DoctorFinderService()
    monkeypatch.setattr(
        "services.doctor_service.requests.get",
        lambda *args, **kwargs: FakeResponse(None, 429),
    )
    result = service.find_doctors(location_text="Hyderabad")
    assert result["status"] == "rate_limited"


def test_api_search_uses_service(client, monkeypatch):
    def fake_find(**kwargs):
        return {
            "status": "success",
            "location_name": "Testville",
            "results": [{"name": "Test Clinic", "type": "clinic", "phone": "Not listed"}],
            "attribution": "Map data (c) OpenStreetMap contributors",
        }

    monkeypatch.setattr("routes.doctor.doctor_service.find_doctors", fake_find)
    response = client.post(
        "/api/doctors/search",
        data=json.dumps({"location": "Testville"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.get_json()["results"][0]["name"] == "Test Clinic"


def test_finder_page_loads(client):
    response = client.get("/doctors")
    assert response.status_code == 200
    assert b"Use my location" in response.data or b"Near Me" in response.data
    assert b"OpenStreetMap" in response.data
