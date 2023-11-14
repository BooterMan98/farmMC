from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)

def test_home_200():
    response = client.get("/")
    assert response.status_code == 200

def test_home_hello():
    response = client.get("/")
    value = response.json()
    assert value["Hello"] == "World"

def test_post_users_200():
    response = client.post("/users?id=test")
    assert response.status_code == 200

def test_post_users_404():
    response = client.post("/users")
    assert response.status_code == 422

def test_get_users_200():
    response = client.get("/users")
    assert response.status_code == 200

def test_get_users_posX():
    response = client.get("/users")
    users = response.json()
    assert users[0]["constructions"][0]["posX"] == 0

def test_get_users_id_200():
    response = client.get("/users?id=test")
    assert response.status_code == 200

def test_get_users_id_test():
    response = client.get("/users/test")
    users = response.json()
    assert users["userId"] == "test"

def test_add_plants_200():
    response = client.post("/add_plants")
    assert response.status_code == 200

def test_add_plants_404():
    response = client.post("/add_plants/error")
    assert response.status_code == 404

def test_read_plants_200():
    response = client.get("/plants")
    assert response.status_code == 200

def test_read_plants_arandano():
    response = client.get("/plants")
    plants = response.json()
    assert plants[0]["name"] == "Arandano"

def test_post_plants_200():
    response = client.post("/plants?userId=test&plantName=Arandano&posX=0&posY=0")
    assert response.status_code == 200

def test_post_plants_404():
    response = client.post("/plants?userId=noexiste&plantName=Arandano&posX=0&posY=0")
    assert response.status_code == 404

def test_harvest():
    response = client.post("/harvest", "1422")
    assert response.status_code == 404

def test_delete_users_204():
    response = client.delete("/users/delete/test")
    assert response.status_code == 204

def test_delete_users_500():
    response = client.delete("/users/delete/notfound")
    assert response.status_code == 500