from fastapi import FastAPI
from fastapi.testclient import TestClient

from chocolate_smart_home.main import app


client = TestClient(app)


def test_get_root():
    response = client.get("/")
    assert response.status_code == 200


def test_get_controllers_data():
    response = client.get("/get_controllers_data/")
    assert response.status_code == 200


def test_update_controller_data():
    response = client.post("/update_controller_data/")
    assert response.status_code == 200


def test_get_aggregate_controllers():
    response = client.get("/get_aggregate_controllers/")
    assert response.status_code == 200


def test_get_spaces():
    response = client.get("/get_spaces/")
    assert response.status_code == 200
