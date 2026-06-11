"""
Fixtures partagées pour les tests pytest IFRI MentorLink.
"""
import pytest
from app import create_app
from app.database import db as _db
from app.config.settings import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-secret-key"
    SECRET_KEY = "test-app-secret"
    WTF_CSRF_ENABLED = False


@pytest.fixture(scope="session")
def app():
    """Crée une instance de l'app avec config de test."""
    app = create_app(TestConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """Client HTTP de test Flask."""
    return app.test_client()


@pytest.fixture(scope="function")
def db(app):
    """Session DB pour les tests, rollback après chaque test."""
    with app.app_context():
        yield _db
        _db.session.rollback()


@pytest.fixture
def auth_headers(client):
    """Inscrit et connecte un utilisateur de test, retourne les headers JWT."""
    client.post("/api/auth/register", json={
        "nom": "Test",
        "prenom": "User",
        "email": "test@ifri.bj",
        "password": "Test1234",
        "telephone": "+22900000001",
    })
    resp = client.post("/api/auth/login", json={
        "identifier": "test@ifri.bj",
        "password": "Test1234",
    })
    token = resp.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers2(client):
    """Second utilisateur pour tester les interactions."""
    client.post("/api/auth/register", json={
        "nom": "Mentor",
        "prenom": "Bob",
        "email": "mentor@ifri.bj",
        "password": "Mentor123",
        "telephone": "+22900000002",
    })
    resp = client.post("/api/auth/login", json={
        "identifier": "mentor@ifri.bj",
        "password": "Mentor123",
    })
    token = resp.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}
