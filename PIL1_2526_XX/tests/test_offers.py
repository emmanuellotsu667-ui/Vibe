"""
Tests pytest — Offres & Demandes
"""


def test_create_offer(client, auth_headers):
    resp = client.post("/api/offers", headers=auth_headers, json={
        "matiere": "Algorithmique",
        "description": "Je peux aider en algo.",
        "format": "en ligne",
    })
    assert resp.status_code == 201
    assert resp.get_json()["offer"]["matiere"] == "Algorithmique"


def test_list_offers(client, auth_headers):
    resp = client.get("/api/offers", headers=auth_headers)
    assert resp.status_code == 200
    assert "offers" in resp.get_json()


def test_list_offers_filter(client, auth_headers):
    client.post("/api/offers", headers=auth_headers, json={"matiere": "SQL avancé"})
    resp = client.get("/api/offers?matiere=SQL", headers=auth_headers)
    offers = resp.get_json()["offers"]
    assert any("SQL" in o["matiere"] for o in offers)


def test_delete_offer(client, auth_headers):
    r = client.post("/api/offers", headers=auth_headers,
                    json={"matiere": "Réseaux"})
    offer_id = r.get_json()["offer"]["id"]
    resp = client.delete(f"/api/offers/{offer_id}", headers=auth_headers)
    assert resp.status_code == 200


def test_delete_offer_forbidden(client, auth_headers, auth_headers2):
    r = client.post("/api/offers", headers=auth_headers,
                    json={"matiere": "C++"})
    offer_id = r.get_json()["offer"]["id"]
    resp = client.delete(f"/api/offers/{offer_id}", headers=auth_headers2)
    assert resp.status_code == 403


def test_create_demand(client, auth_headers):
    resp = client.post("/api/demands", headers=auth_headers, json={
        "matiere": "Deep Learning",
        "format": "les deux",
    })
    assert resp.status_code == 201


def test_list_demands(client, auth_headers):
    resp = client.get("/api/demands", headers=auth_headers)
    assert resp.status_code == 200
    assert "demands" in resp.get_json()
