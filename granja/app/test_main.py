from fastapi import FastAPI
from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)

def test_read_plants():
    response = client.get("plants")
    assert response.status_code == 200
    plants = response.json()
    assert plants[0]["id"] == "65401e4bfe1ebc983d3df03a"