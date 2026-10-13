import json
from models.user import User
from models.assessment import Assessment

def test_home_page(client):
    """Test that the homepage renders successfully with symptoms loaded."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"MediGuide" in response.data
    assert b"itching" in response.data
    assert b"Symptom Checker" in response.data

def test_register_success(client, app):
    """Test successful user registration."""
    response = client.post("/register", data={
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Account created successfully" in response.data

    with app.app_context():
        user = User.query.filter_by(email="jane@example.com").first()
        assert user is not None
        assert user.name == "Jane Doe"
        assert user.check_password("Password123!")

def test_register_duplicate_email(client):
    """Test that duplicate registration with same email is rejected."""
    client.post("/register", data={
        "name": "First User",
        "email": "duplicate@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    })
    response = client.post("/register", data={
        "name": "Second User",
        "email": "duplicate@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"account with that email already exists" in response.data

def test_register_password_mismatch(client):
    """Test that registration with mismatched passwords fails."""
    response = client.post("/register", data={
        "name": "Mismatch User",
        "email": "mismatch@example.com",
        "password": "Password123!",
        "confirm_password": "DifferentPassword!"
    }, follow_redirects=True)
    assert b"Passwords do not match" in response.data

def test_login_success_and_dashboard_access(client, auth_user):
    """Test login with valid credentials and redirect to dashboard."""
    response = client.post("/login", data={
        "email": "patient@example.com",
        "password": "SecurePass123!"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome back!" in response.data
    assert b"Welcome, Test Patient!" in response.data

def test_login_failure_invalid_password(client, auth_user):
    """Test login fails with wrong password."""
    response = client.post("/login", data={
        "email": "patient@example.com",
        "password": "WrongPassword!"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data

def test_dashboard_unauthorized(client):
    """Test protected dashboard redirects to login when not authenticated."""
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

def test_logout(client, auth_user):
    """Test logout clears session."""
    client.post("/login", data={
        "email": "patient@example.com",
        "password": "SecurePass123!"
    })
    response = client.post("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"You have been logged out" in response.data

    # Try dashboard again - should redirect
    dashboard_res = client.get("/dashboard", follow_redirects=False)
    assert dashboard_res.status_code == 302

def test_predict_symptoms_success(client):
    """Test symptom prediction API returns top 3 predictions and disclaimers."""
    response = client.post(
        "/predict",
        data=json.dumps({"symptoms": ["itching", "skin_rash"]}),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "results" in data
    assert len(data["results"]) == 3
    assert "disease" in data["results"][0]
    assert "confidence" in data["results"][0]
    assert "urgency" in data
    assert "disclaimer" in data

def test_predict_symptoms_invalid_input(client):
    """Test prediction endpoint with empty or invalid symptoms."""
    # Empty symptoms
    r1 = client.post(
        "/predict",
        data=json.dumps({"symptoms": []}),
        content_type="application/json"
    )
    assert r1.status_code == 400
    assert b"Please select at least one symptom" in r1.data

    # Invalid symptom name
    r2 = client.post(
        "/predict",
        data=json.dumps({"symptoms": ["non_existent_symptom_12345"]}),
        content_type="application/json"
    )
    assert r2.status_code == 400
    assert b"Invalid symptom" in r2.data
