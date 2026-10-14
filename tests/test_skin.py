def test_skin_health_guide_page(client):
    response = client.get("/skin-health")
    assert response.status_code == 200
    body = response.data
    assert b"Skin Health Guide" in body
    assert b"ABCDE" in body
    assert b"dermatologist" in body
    assert b"future scope" in body.lower() or b"Future scope" in body
    assert b"Inspection Pipeline Results" not in body
    assert b"Token" not in body
    assert b"analyze" not in body.lower() or b"Photo analysis is future scope" in body


def test_old_skin_analysis_url_redirects(client):
    response = client.get("/skin-analysis", follow_redirects=False)
    assert response.status_code == 301
    assert "/skin-health" in response.headers["Location"]


def test_homepage_does_not_advertise_skin_analysis(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Inspection Pipeline" not in response.data
    assert b"Skin Health Guide" in response.data
