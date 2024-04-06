from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from chocolate_smart_home.main import app
import chocolate_smart_home.schemas as schemas


client = TestClient(app)


def test_create_device_type(test_database):
    resp = client.post(
        "/create_device_type/",
        json={"name": "test_device_type_name"},
    )

    assert resp.status_code == 200

    data = resp.json()
    device_type = schemas.DeviceType(**data)
    assert data["name"] == "test_device_type_name"


def test_create_duplicate_device_type_fails(test_database):
    device_type_name = "test_device_type_name"
    resp = client.post("/create_device_type/", json={"name": device_type_name})
    resp = client.post("/create_device_type/", json={"name": device_type_name})

    assert resp.status_code == 500

    assert resp.json() == { "detail": "Key (name)=(test_device_type_name) already exists." }


def test_create_device_type_methods_not_allowed(test_database):
    url = "/create_device_type/"
    assert 405 == client.get(url).status_code
    assert 405 == client.delete(url).status_code
    assert 405 == client.patch(url, json={}).status_code
