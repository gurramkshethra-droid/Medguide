import json

from services.followup import apply_answers, suggest_followup_questions
from services.symptom_engine import symptom_engine


def test_followup_questions_are_yes_no_separators():
    questions = suggest_followup_questions(
        symptom_engine,
        ["itching", "skin_rash", "nodal_skin_eruptions"],
        ["Fungal infection", "Drug Reaction", "Psoriasis"],
        count=3,
    )
    assert 1 <= len(questions) <= 3
    for item in questions:
        assert item["question"].endswith("?")
        assert item["symptom"] not in {
            "itching", "skin_rash", "nodal_skin_eruptions"
        }


def test_invalid_followup_answer_rejected(client):
    response = client.post(
        "/predict/follow-up",
        data=json.dumps({
            "symptoms": ["itching", "skin_rash", "nodal_skin_eruptions"],
            "answers": {"dischromic _patches": "maybe"},
        }),
        content_type="application/json",
    )
    assert response.status_code == 400
    assert b"yes or no" in response.data


def test_followup_yes_reruns_and_reports_ranking_change(client):
    first = client.post(
        "/predict",
        data=json.dumps({"symptoms": ["itching", "skin_rash", "nodal_skin_eruptions"]}),
        content_type="application/json",
    ).get_json()
    assert first["followup_questions"]
    symptom = first["followup_questions"][0]["symptom"]
    response = client.post(
        "/predict/follow-up",
        data=json.dumps({
            "symptoms": ["itching", "skin_rash", "nodal_skin_eruptions"],
            "answers": {symptom: "yes"},
        }),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "ranking_change" in data
    assert "previous_results" in data
    assert symptom in data["selected_symptoms"]
    assert data["applied_answers"][symptom] == "yes"


def test_apply_answers_yes_adds_symptom():
    updated, applied = apply_answers(["cough", "headache", "fatigue"], {"high_fever": "yes"})
    assert "high_fever" in updated
    assert applied["high_fever"] == "yes"


def test_apply_answers_invalid():
    try:
        apply_answers(["cough"], {"high_fever": "sometimes"})
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "yes or no" in str(exc)
