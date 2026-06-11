"""
Tests pytest — Module Auth
"""
import pytest


def test_register_success(client):
    resp = client.post("/api/auth/register", json={
        "nom": "Dupont",
        "prenom": "Alice",
        "email": "alice@ifri.bj",
        "password": "Alice1234",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert "token" in data
    assert data["user"]["email"] == "alice@ifri.bj"


def test_register_duplicate_email(client):
    payload = {"nom": "A", "prenom": "B", "email": "dup@ifri.bj", "password": "Pass1234"}
    client.post("/api/auth/register", json=payload)
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 409


def test_register_missing_fields(client):
    resp = client.post("/api/auth/register", json={"email": "x@ifri.bj"})
    assert resp.status_code == 400


def test_register_short_password(client):
    resp = client.post("/api/auth/register", json={
        "nom": "A", "prenom": "B", "email": "short@ifri.bj", "password": "123"
    })
    assert resp.status_code == 400


def test_login_success(client, auth_headers):
    resp = client.post("/api/auth/login", json={
        "identifier": "test@ifri.bj",
        "password": "Test1234",
    })
    assert resp.status_code == 200
    assert "token" in resp.get_json()


def test_login_wrong_password(client):
    resp = client.post("/api/auth/login", json={
        "identifier": "test@ifri.bj",
        "password": "WrongPass",
    })
    assert resp.status_code == 401


def test_me_authenticated(client, auth_headers):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["user"]["email"] == "test@ifri.bj"


def test_me_unauthenticated(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_health_endpoint(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"
