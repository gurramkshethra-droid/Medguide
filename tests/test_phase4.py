import json
import pytest
from models.user import User
from models.assessment import Assessment
from extensions import db

@pytest.fixture
def second_user(app):
    with app.app_context():
        user = User(
            name="Second Patient",
            email="second@example.com",
            role="user",
            consent_save_history=True
        )
        user.set_password("SecondPass123!")
        db.session.add(user)
        db.session.commit()
        return user.id

@pytest.fixture
def admin_user(app):
    with app.app_context():
        admin = User(
            name="System Admin",
            email="admin@mediguide.ai",
            role="admin",
            consent_save_history=False
        )
        admin.set_password("AdminSecurePass123!")
        db.session.add(admin)
        db.session.commit()
        return admin.id


def test_profile_update_info(client, auth_user):
    """Test updating user profile name and privacy consent."""
    client.post("/login", data={"email": "patient@example.com", "password": "SecurePass123!"})
    
    # Update name and toggle consent off
    response = client.post("/profile", data={
        "action": "update_info",
        "name": "Jane Patient Updated",
        # consent_save_history omitted = checkbox unchecked
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Profile information and privacy preferences updated" in response.data

    with client.application.app_context():
        user = db.session.get(User, auth_user)
        assert user.name == "Jane Patient Updated"
        assert user.consent_save_history is False


def test_profile_change_password_success(client, auth_user):
    """Test user successfully changing their password."""
    client.post("/login", data={"email": "patient@example.com", "password": "SecurePass123!"})

    response = client.post("/profile", data={
        "action": "change_password",
        "current_password": "SecurePass123!",
        "new_password": "BrandNewPassword123!",
        "confirm_password": "BrandNewPassword123!"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Password updated successfully" in response.data

    # Log out and log back in with new password
    client.post("/logout")
    login_res = client.post("/login", data={
        "email": "patient@example.com",
        "password": "BrandNewPassword123!"
    }, follow_redirects=True)
    assert b"Welcome back!" in login_res.data


def test_profile_change_password_invalid_current(client, auth_user):
    """Test password change fails when current password is wrong."""
    client.post("/login", data={"email": "patient@example.com", "password": "SecurePass123!"})

    response = client.post("/profile", data={
        "action": "change_password",
        "current_password": "IncorrectPassword!",
        "new_password": "BrandNewPassword123!",
        "confirm_password": "BrandNewPassword123!"
    }, follow_redirects=True)

    assert b"Current password is incorrect" in response.data


def test_consent_setting_effect_on_predict(client, auth_user):
    """Test that assessments are saved ONLY when user has granted consent."""
    client.post("/login", data={"email": "patient@example.com", "password": "SecurePass123!"})

    # auth_user starts with consent_save_history=True
    r1 = client.post("/predict", data=json.dumps({"symptoms": ["itching", "skin_rash", "nodal_skin_eruptions"]}), content_type="application/json")
    assert r1.status_code == 200

    with client.application.app_context():
        assert Assessment.query.filter_by(user_id=auth_user).count() == 1

    # Turn consent OFF
    client.post("/profile", data={"action": "update_info", "name": "Test Patient"})

    # Check symptoms again with consent off
    r2 = client.post("/predict", data=json.dumps({"symptoms": ["continuous_sneezing", "shivering", "chills"]}), content_type="application/json")
    assert r2.status_code == 200

    with client.application.app_context():
        # Count must remain 1 - second assessment was ephemeral
        assert Assessment.query.filter_by(user_id=auth_user).count() == 1


def test_history_view_and_single_delete(client, auth_user):
    """Test viewing and deleting single assessment from history."""
    client.post("/login", data={"email": "patient@example.com", "password": "SecurePass123!"})
    client.post("/predict", data=json.dumps({"symptoms": ["itching", "skin_rash", "nodal_skin_eruptions"]}), content_type="application/json")

    # View history
    history_res = client.get("/history")
    assert history_res.status_code == 200
    assert b"My Assessment History" in history_res.data
    assert b"itching" in history_res.data

    with client.application.app_context():
        assessment = Assessment.query.filter_by(user_id=auth_user).first()
        assessment_id = assessment.id

    # Delete single assessment
    del_res = client.post(f"/history/{assessment_id}/delete", follow_redirects=True)
    assert del_res.status_code == 200
    assert b"Assessment record deleted" in del_res.data

    with client.application.app_context():
        assert db.session.get(Assessment, assessment_id) is None


def test_cross_user_assessment_delete_forbidden(client, auth_user, second_user):
    """SECURITY TEST: User B must not delete User A's assessment (403 Forbidden)."""
    # Create assessment for User A (auth_user)
    client.post("/login", data={"email": "patient@example.com", "password": "SecurePass123!"})
    client.post("/predict", data=json.dumps({"symptoms": ["itching", "skin_rash", "nodal_skin_eruptions"]}), content_type="application/json")
    client.post("/logout")

    with client.application.app_context():
        user_a_assessment = Assessment.query.filter_by(user_id=auth_user).first()
        assert user_a_assessment is not None
        user_a_assessment_id = user_a_assessment.id

    # Log in as User B (second_user)
    client.post("/login", data={"email": "second@example.com", "password": "SecondPass123!"})

    # Attempt to delete User A's assessment
    malicious_del = client.post(f"/history/{user_a_assessment_id}/delete")
    assert malicious_del.status_code == 403

    # Verify User A's assessment was NOT deleted
    with client.application.app_context():
        check_assessment = db.session.get(Assessment, user_a_assessment_id)
        assert check_assessment is not None
        assert check_assessment.user_id == auth_user


def test_history_clear_all_isolation(client, auth_user, second_user):
    """Test clear-all deletes only the requesting user's records."""
    # User A assessment
    client.post("/login", data={"email": "patient@example.com", "password": "SecurePass123!"})
    client.post("/predict", data=json.dumps({"symptoms": ["itching", "skin_rash", "nodal_skin_eruptions"]}), content_type="application/json")
    client.post("/logout")

    # User B assessment
    client.post("/login", data={"email": "second@example.com", "password": "SecondPass123!"})
    client.post("/predict", data=json.dumps({"symptoms": ["continuous_sneezing", "shivering", "chills"]}), content_type="application/json")

    # User B clears all history
    client.post("/history/clear-all", follow_redirects=True)

    with client.application.app_context():
        # User B should have 0 assessments
        assert Assessment.query.filter_by(user_id=second_user).count() == 0
        # User A assessment must be intact
        assert Assessment.query.filter_by(user_id=auth_user).count() == 1


def test_admin_access_unauthorized_guest(client):
    """Unauthenticated guest accessing /admin must be redirected to login."""
    response = client.get("/admin", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_admin_access_forbidden_regular_user(client, auth_user):
    """Regular user accessing /admin must be rejected with 403 Forbidden."""
    client.post("/login", data={"email": "patient@example.com", "password": "SecurePass123!"})
    response = client.get("/admin")
    assert response.status_code == 403


def test_admin_access_success_for_admin(client, admin_user):
    """Admin user accessing /admin must succeed with 200 OK."""
    client.post("/login", data={"email": "admin@mediguide.ai", "password": "AdminSecurePass123!"})
    response = client.get("/admin")
    assert response.status_code == 200
    assert b"Administrator Oversight Portal" in response.data
    assert b"Registered Users" in response.data


def test_admin_toggle_user_status(client, admin_user, auth_user):
    """Admin can deactivate and activate regular users; deactivated users cannot log in."""
    client.post("/login", data={"email": "admin@mediguide.ai", "password": "AdminSecurePass123!"})

    # Deactivate regular user
    toggle_res = client.post(f"/admin/user/{auth_user}/toggle-status", follow_redirects=True)
    assert toggle_res.status_code == 200
    assert b"deactivated" in toggle_res.data

    with client.application.app_context():
        user = db.session.get(User, auth_user)
        assert user.is_active is False

    # Logout admin
    client.post("/logout")

    # Attempt login as deactivated user - must fail
    login_attempt = client.post("/login", data={
        "email": "patient@example.com",
        "password": "SecurePass123!"
    }, follow_redirects=True)
    assert b"Your account has been deactivated" in login_attempt.data


def test_user_delete_account(client, auth_user):
    """Test user self-service account deletion with password confirmation."""
    client.post("/login", data={"email": "patient@example.com", "password": "SecurePass123!"})

    response = client.post("/profile/delete-account", data={
        "password": "SecurePass123!"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Your account and all associated assessment records have been deleted" in response.data

    with client.application.app_context():
        assert db.session.get(User, auth_user) is None


def test_csrf_protection_when_enabled(app):
    """Test that CSRF protection rejects state-changing requests when enabled."""
    app.config["WTF_CSRF_ENABLED"] = True
    test_client = app.test_client()

    # POST to /login without CSRF token
    response = test_client.post("/login", data={
        "email": "someone@example.com",
        "password": "SomePassword123!"
    })
    # Must fail with 400 Bad Request due to missing CSRF token
    assert response.status_code == 400
