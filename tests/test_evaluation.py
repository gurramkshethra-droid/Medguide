def test_evaluation_page(client):
    response = client.get("/evaluation")
    assert response.status_code == 200
    body = response.data
    assert b"test accuracy" in body.lower() or b"Test accuracy" in body
    assert b"Top-3" in body or b"top-3" in body
    assert b"cross-validation" in body.lower() or b"Cross-validation" in body
    assert b"duplicate" in body.lower()
    assert b"no age" in body.lower() or b"no age, gender" in body.lower()
    assert b"confusion" in body.lower()
