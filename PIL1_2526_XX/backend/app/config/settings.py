"""
Configuration de l'application Flask.
Supporte les modes Development et Production.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration de base commune à tous les environnements."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-fallback")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-fallback")
    JWT_EXPIRATION_HOURS = 24

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/ifri_mentorlink"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    CORS_ORIGINS = [FRONTEND_URL, "http://localhost:5000", "http://127.0.0.1:5500"]


class DevelopmentConfig(Config):
    """Configuration pour l'environnement de développement."""
    DEBUG = True
    SQLALCHEMY_ECHO = False  # Mettre True pour voir les requêtes SQL


class ProductionConfig(Config):
    """Configuration pour l'environnement de production."""
    DEBUG = False
    SQLALCHEMY_ECHO = False


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config():
    env = os.getenv("FLASK_ENV", "development")
    return config_map.get(env, DevelopmentConfig)
