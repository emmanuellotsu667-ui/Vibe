"""
Tests pytest — Module Profil
"""


def test_get_profile(client, auth_headers):
    resp = client.get("/api/profile/", headers=auth_headers)
    assert resp.status_code == 200
    assert "profile" in resp.get_json()


def test_update_profile(client, auth_headers):
    resp = client.put("/api/profile/", headers=auth_headers, json={
        "filiere": "IA",
        "niveau": "L3",
        "bio": "Passionné d'IA.",
    })
    assert resp.status_code == 200
    data = resp.get_json()["profile"]
    assert data["filiere"] == "IA"
    assert data["niveau"] == "L3"


def test_add_competence(client, auth_headers):
    resp = client.post("/api/profile/competences", headers=auth_headers, json={
        "matiere": "Machine Learning",
        "niveau_maitrise": 4,
    })
    assert resp.status_code == 201
    assert resp.get_json()["competence"]["matiere"] == "Machine Learning"


def test_delete_competence(client, auth_headers):
    r = client.post("/api/profile/competences", headers=auth_headers,
                    json={"matiere": "Python", "niveau_maitrise": 3})
    comp_id = r.get_json()["competence"]["id"]
    resp = client.delete(f"/api/profile/competences/{comp_id}", headers=auth_headers)
    assert resp.status_code == 200


def test_add_lacune(client, auth_headers):
    resp = client.post("/api/profile/lacunes", headers=auth_headers,
                       json={"matiere": "Deep Learning"})
    assert resp.status_code == 201


def test_add_disponibilite(client, auth_headers):
    resp = client.post("/api/profile/disponibilites", headers=auth_headers, json={
        "jour": "Lundi",
        "heure_debut": "08:00",
        "heure_fin": "10:00",
    })
    assert resp.status_code == 201
    assert resp.get_json()["disponibilite"]["jour"] == "Lundi"


def test_add_disponibilite_bad_time(client, auth_headers):
    resp = client.post("/api/profile/disponibilites", headers=auth_headers, json={
        "jour": "Mardi",
        "heure_debut": "NOT_TIME",
        "heure_fin": "10:00",
    })
    assert resp.status_code == 400
