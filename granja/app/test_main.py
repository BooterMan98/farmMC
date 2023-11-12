from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_users():
    response = client.get("/users")
    assert response.status_code == 200

def test_get_plants():
    response = client.get("/plants")
    assert response.status_code == 200
