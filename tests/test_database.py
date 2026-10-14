import json

from sqlalchemy import inspect as sa_inspect

from extensions import db
from models.assessment import Assessment
from models.user import User


def test_sqlite_tables_exist(app):
    with app.app_context():
        tables = set(sa_inspect(db.engine).get_table_names())
        assert "users" in tables
        assert "assessments" in tables
        assert "audit_logs" in tables


def test_assessment_persists_for_consenting_user(client, auth_user, app):
    client.post("/login", data={"email": "patient@example.com", "password": "SecurePass123!"})
    response = client.post(
        "/predict",
        data=json.dumps({"symptoms": ["itching", "skin_rash", "nodal_skin_eruptions"]}),
        content_type="application/json",
    )
    assert response.status_code == 200
    with app.app_context():
        rows = Assessment.query.filter_by(user_id=auth_user).all()
        assert len(rows) == 1
        assert rows[0].top_disease
        assert "itching" in rows[0].symptoms_json
        owner = db.session.get(User, auth_user)
        assert owner.email == "patient@example.com"
