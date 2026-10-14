import json


def test_headache_does_not_rank_stroke_or_aids(client):
    response = client.post(
        "/predict",
        data=json.dumps({"symptoms": ["headache"]}),
        content_type="application/json",
    )
    assert response.status_code == 200
    diseases = [item["disease"] for item in response.get_json()["results"]]
    assert "Paralysis (brain hemorrhage)" not in diseases
    assert "AIDS" not in diseases
    assert "Urinary tract infection" not in diseases


def test_cold_symptoms_prefer_respiratory_conditions(client):
    response = client.post(
        "/predict",
        data=json.dumps({
            "symptoms": ["continuous_sneezing", "runny_nose", "cough"],
            "duration": "1_to_3_days",
            "severity": "mild",
            "age_group": "adult",
        }),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    top = data["results"][0]["disease"]
    assert top in {"Common Cold", "Allergy", "Bronchial Asthma"}
    ranked = [item["disease"] for item in data["results"]]
    assert "AIDS" not in ranked
    assert "Paralysis (brain hemorrhage)" not in ranked


def test_safety_runs_before_guidance_for_chest_pain(client):
    response = client.post(
        "/predict",
        data=json.dumps({
            "symptoms": ["chest_pain", "sweating", "breathlessness"],
            "severity": "severe",
            "age_group": "older_adult",
            "history": ["heart_disease"],
        }),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["safety"]["level"] == "emergency"
    assert data["safety"]["checked_before_guidance"] is True
    assert "emergency_alert" in data


def test_symptom_name_mapping_accepts_spaced_labels(client):
    response = client.post(
        "/predict",
        data=json.dumps({"symptoms": ["skin rash", "itching", "nodal skin eruptions"]}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["results"][0]["disease"] == "Fungal infection"
