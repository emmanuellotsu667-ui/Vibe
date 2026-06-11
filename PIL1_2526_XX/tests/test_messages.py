"""
Tests pytest — Messagerie
"""


def test_create_conversation(client, auth_headers, auth_headers2):
    # Obtenir l'ID du second utilisateur
    r = client.get("/api/auth/me", headers=auth_headers2)
    user2_id = r.get_json()["user"]["id"]

    resp = client.post("/api/messages/conversations", headers=auth_headers,
                       json={"user_id": user2_id})
    assert resp.status_code in (200, 201)
    assert "conversation" in resp.get_json()


def test_create_conversation_same_user(client, auth_headers):
    r = client.get("/api/auth/me", headers=auth_headers)
    my_id = r.get_json()["user"]["id"]
    resp = client.post("/api/messages/conversations", headers=auth_headers,
                       json={"user_id": my_id})
    assert resp.status_code == 400


def test_list_conversations(client, auth_headers):
    resp = client.get("/api/messages/conversations", headers=auth_headers)
    assert resp.status_code == 200
    assert "conversations" in resp.get_json()


def test_send_message(client, auth_headers, auth_headers2):
    r2 = client.get("/api/auth/me", headers=auth_headers2)
    user2_id = r2.get_json()["user"]["id"]
    conv = client.post("/api/messages/conversations", headers=auth_headers,
                       json={"user_id": user2_id}).get_json()["conversation"]
    conv_id = conv["id"]

    resp = client.post(f"/api/messages/conversations/{conv_id}/send",
                       headers=auth_headers, json={"content": "Bonjour !"})
    assert resp.status_code == 201
    assert resp.get_json()["message"]["content"] == "Bonjour !"


def test_send_empty_message(client, auth_headers, auth_headers2):
    r2 = client.get("/api/auth/me", headers=auth_headers2)
    user2_id = r2.get_json()["user"]["id"]
    conv = client.post("/api/messages/conversations", headers=auth_headers,
                       json={"user_id": user2_id}).get_json()["conversation"]
    resp = client.post(f"/api/messages/conversations/{conv['id']}/send",
                       headers=auth_headers, json={"content": ""})
    assert resp.status_code == 400
