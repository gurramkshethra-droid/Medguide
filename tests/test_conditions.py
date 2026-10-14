from services.health_data import health_service
from services.ml_service import ml_service


def test_every_model_class_has_condition_entry():
    classes = ml_service.get_classes()
    missing = []
    for name in classes:
        info = health_service.get_condition_by_key(name)
        if not info:
            missing.append(name)
            continue
        assert info["slug"]
        assert info["description"]
        assert info["homecare"]
        assert "pharmacist" in info["pharmacist_otc"].lower()
        assert info["when_to_seek_care"]
        assert info["warning_signs"]
        assert info["specialty"]
        assert info["sources"]
    assert missing == []


def test_gerd_slug_page(client):
    response = client.get("/conditions/gerd")
    assert response.status_code == 200
    assert b"Gastroesophageal" in response.data or b"GERD" in response.data
    assert b"Ask a pharmacist" in response.data
    assert b"Homecare" in response.data or b"Home care" in response.data or b"homecare" in response.data.lower()


def test_unknown_condition_404(client):
    response = client.get("/conditions/not-a-real-slug")
    assert response.status_code == 404
