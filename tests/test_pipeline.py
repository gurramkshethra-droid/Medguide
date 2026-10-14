import json

import pandas as pd

from services.ml_service import ml_service
from services.symptom_engine import MIN_SYMPTOMS, symptom_engine


def test_min_three_symptoms_required(client):
    response = client.post(
        "/predict",
        data=json.dumps({"symptoms": ["headache", "fatigue"]}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["needs_more_symptoms"] is True
    assert data["results"] == []
    assert "add more symptoms" in data["message"].lower()


def test_empty_symptoms_rejected(client):
    response = client.post(
        "/predict",
        data=json.dumps({"symptoms": []}),
        content_type="application/json",
    )
    assert response.status_code == 400


def test_feature_frame_uses_saved_order():
    frame = ml_service.build_feature_frame(["itching", "skin_rash"])
    assert list(frame.columns) == ml_service.symptoms
    assert frame.shape == (1, len(ml_service.symptoms))
    assert int(frame.loc[0, "itching"]) == 1
    assert int(frame.loc[0, "skin_rash"]) == 1
    assert int(frame.loc[0, "cough"]) == 0


def test_website_pipeline_matches_direct_model_on_10_training_rows():
    df = pd.read_csv("Training.csv")
    df = df.loc[:, ~df.columns.str.contains(r"^Unnamed")]
    features = ml_service.symptoms
    sample = df.drop_duplicates(subset=features + ["prognosis"]).head(10)
    assert len(sample) == 10

    for _, row in sample.iterrows():
        chosen = [name for name in features if int(row[name]) == 1]
        assert len(chosen) >= MIN_SYMPTOMS
        frame = pd.DataFrame([[int(row[name]) for name in features]], columns=features)
        direct = str(ml_service.model.predict(frame)[0])
        website = symptom_engine.analyze(ml_service, chosen, top_k=3)
        assert website["ml_top_disease"] == direct
        assert website["results"][0]["disease"] == direct
        assert "matched_symptoms" in website["results"][0]
        assert "unreported_typical_symptoms" in website["results"][0]


def test_top_three_include_match_fields(client):
    response = client.post(
        "/predict",
        data=json.dumps({
            "symptoms": ["itching", "skin_rash", "nodal_skin_eruptions"],
            "severity": "mild",
        }),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["results"]
    first = data["results"][0]
    assert "matched_symptoms" in first
    assert "unreported_typical_symptoms" in first
    assert "itching" in " ".join(first["matched_symptoms"])
