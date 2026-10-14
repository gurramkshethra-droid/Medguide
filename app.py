import os
from flask import Flask
from flask_wtf.csrf import generate_csrf
from dotenv import load_dotenv

from config import config_by_name
from extensions import db, csrf, limiter
from auth.routes import auth_bp
from routes.main import main_bp
from routes.symptom import symptom_bp
from routes.errors import errors_bp
from routes.admin import admin_bp
from routes.conditions import conditions_bp
from routes.doctor import doctor_bp
from routes.skin import skin_bp
from routes.evaluation import evaluation_bp
import click

load_dotenv()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "default")

    app = Flask(__name__)
    app.config.from_object(
        config_by_name.get(config_name, config_by_name["default"])
    )

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(symptom_bp)
    app.register_blueprint(errors_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(conditions_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(skin_bp)
    app.register_blueprint(evaluation_bp)

    # Context processor for CSRF token string compatibility across all templates
    @app.context_processor
    def inject_csrf_token():
        return {"csrf_token": generate_csrf()}

    # Attach SQLAlchemy models to the configured database without dropping records
    with app.app_context():
        import models  # Ensure all models are imported before create_all
        db.create_all()
        app.logger.info("Database attached: %s", app.config.get("SQLALCHEMY_DATABASE_URI"))

    # CLI Command to securely bootstrap the initial administrator
    @app.cli.command("create-admin")
    @click.option("--name", default="Administrator", help="Admin user name")
    @click.option("--email", prompt="Admin email", help="Admin email address")
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="Admin password")
    def create_admin_cmd(name, email, password):
        from models.user import User
        email = email.strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            user.role = "admin"
            user.set_password(password)
            db.session.commit()
            click.echo(f"Existing user '{email}' elevated to administrator.")
        else:
            admin = User(name=name, email=email, role="admin", is_active=True)
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            click.echo(f"New administrator account created for '{email}'.")

    return app

# Application instance for WSGI / local execution
app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=False,
        use_reloader=False
    )


