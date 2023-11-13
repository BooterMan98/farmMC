from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)

def test_post_users_200():
    response = client.post("/users?id=0")
    assert response.status_code == 200

def test_read_plants():
    response = client.get("/plants")
    assert response.status_code == 200
    plants = response.json()
    assert plants[0]["id"] == "65401e4bfe1ebc983d3df03a"

def test_home_200():
    response = client.get("/")
    assert response.status_code == 200


def test_home_hello():
    response = client.get("/")
    value = response.json()
    print(value)
    assert value["Hello"] == "World"

def test_harvest():
    response = client.post("/harvest", "1422")
    assert response.status_code == 404

def test_post_plants_200():
    response = client.post("/plants?userId=1&plantName=Arandano&posX=0&posY=0")
    assert response.status_code == 200

def test_post_plants_404():
    response = client.post("/plants?userId=a&plantName=Arandano&posX=0&posY=0")
    assert response.status_code == 404

