from services.triage import EMERGENCY, ROUTINE, URGENT, assess_triage


def test_emergency_chest_pain_with_breathlessness():
    result = assess_triage(["chest_pain", "breathlessness"], severity="moderate")
    assert result["level"] == EMERGENCY
    assert result["checked_before_guidance"] is True
    assert result["overrides_model"] is True


def test_emergency_severe_breathing():
    result = assess_triage(["breathlessness"], severity="severe")
    assert result["level"] == EMERGENCY


def test_emergency_fainting():
    result = assess_triage(["coma"], severity="moderate")
    assert result["level"] == EMERGENCY


def test_emergency_confusion():
    result = assess_triage(["altered_sensorium"], severity="moderate")
    assert result["level"] == EMERGENCY


def test_emergency_serious_bleeding():
    result = assess_triage(["stomach_bleeding"], severity="mild")
    assert result["level"] == EMERGENCY


def test_urgent_yellow_eyes_fever_vomiting():
    result = assess_triage(
        ["yellowing_of_eyes", "high_fever", "vomiting"],
        severity="moderate",
    )
    assert result["level"] == URGENT
    assert result["overrides_model"] is True


def test_routine_common_cold_cluster():
    result = assess_triage(
        ["continuous_sneezing", "runny_nose", "cough"],
        severity="mild",
    )
    assert result["level"] == ROUTINE


def test_triage_banner_not_overridden_by_model(client):
    import json

    response = client.post(
        "/predict",
        data=json.dumps({
            "symptoms": ["chest_pain", "breathlessness", "sweating"],
            "severity": "severe",
        }),
        content_type="application/json",
    )
    data = response.get_json()
    assert data["safety"]["level"] == EMERGENCY
    assert "emergency_alert" in data
