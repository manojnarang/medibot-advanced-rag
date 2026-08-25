def test_login_success(client):
    response = client.post("/login", json={"username": "dr.mehta", "password": "Doctor@123"})
    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "doctor"
    assert "clinical" in body["accessible_collections"]
    assert "billing" not in body["accessible_collections"]
    assert body["access_token"]


def test_login_wrong_password(client):
    response = client.post("/login", json={"username": "dr.mehta", "password": "wrong"})
    assert response.status_code == 401


def test_login_unknown_user(client):
    response = client.post("/login", json={"username": "nobody", "password": "x"})
    assert response.status_code == 401


def test_chat_requires_auth(client):
    response = client.post("/chat", json={"question": "hello"})
    assert response.status_code == 401
