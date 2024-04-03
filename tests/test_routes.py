from fastapi import FastAPI
from fastapi.testclient import TestClient

from chocolate_smart_home.main import app
import chocolate_smart_home.schemas as schemas


client = TestClient(app)


def test_create_device_type(test_database):
    response = client.post(
        "/create_device_type/",
        json={"name": "test_device_type_name"},
    )

    assert response.status_code == 200

    data = response.json()
    device_type = schemas.DeviceType(**data)
    assert data["name"] == "test_device_type_name"


def test_create_device_type_get_not_allowed(test_database):
    assert 405 == client.get("/create_device_type/").status_code


def test_create_device_type_patch_not_allowed(test_database):
    assert 405 == client.patch("/create_device_type/", json={}).status_code


def test_create_device(test_database):
    response = client.post(
        "/create_device/",
        json={
            "mqtt_id": 0,
            "device_type_name": "test_device_type_name",
            "remote_name": "Test Device - 123",
            "name": "",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["mqtt_id"] == 0
    assert data["device_type"]["name"] == "test_device_type_name"
    assert data["remote_name"] == "Test Device - 123"
    assert data["name"] == ""


def test_create_device_get_not_allowed(test_database):
    assert 405 == client.get("/create_device/").status_code


def test_create_device_patch_not_allowed(test_database):
    assert 405 == client.patch("/create_device/", json={}).status_code
