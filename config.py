import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get(
        "MEDIGUIDE_SECRET_KEY"
    ) or os.environ.get(
        "SECRET_KEY",
        "development-only-change-this-secret-mediguide-pbl-2026"
    )
    
    # Database
    db_url = os.environ.get("DATABASE_URL")
    if db_url and db_url.startswith("postgres://"):
        # Fix Heroku/old postgres dialect string if needed
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = db_url or f"sqlite:///{BASE_DIR / 'mediguide.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session & Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "False").lower() in ("true", "1")
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour

    # File uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max limit
    UPLOAD_FOLDER = str(BASE_DIR / "uploads")

    # Rate Limiting
    RATELIMIT_DEFAULT = "200 per day; 60 per hour"
    RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration with in-memory SQLite and disabled CSRF for test speed."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
