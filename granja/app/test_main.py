from fastapi import FastAPI
from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)

def test_read_plants():
    response = client.get("plants")
    assert response.status_code == 200
    assert response.json()