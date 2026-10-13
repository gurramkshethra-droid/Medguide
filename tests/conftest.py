import pytest
from app import create_app
from extensions import db
from models.user import User

@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_user(app):
    with app.app_context():
        user = User(
            name="Test Patient",
            email="patient@example.com",
            role="user",
            consent_save_history=True
        )
        user.set_password("SecurePass123!")
        db.session.add(user)
        db.session.commit()
        return user.id
