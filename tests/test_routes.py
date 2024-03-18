from fastapi import FastAPI
from fastapi.testclient import TestClient

from chocolate_smart_home.main import app


client = TestClient(app)


def test_get_root():
    response = client.get("/")
    assert response.status_code == 200


def test_get_devices_data():
    response = client.get("/get_devices_data/")
    assert response.status_code == 200


# def test_update_device_data():
#     response = client.post("/update_device_data/")
#     assert response.status_code == 200


def test_get_spaces_data():
    response = client.get("/get_spaces_data/")
    assert response.status_code == 200
