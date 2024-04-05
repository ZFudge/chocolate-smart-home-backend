from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

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


def test_create_device_type_methods_not_allowed(test_database):
    url = "/create_device_type/"
    assert 405 == client.get(url).status_code
    assert 405 == client.delete(url).status_code
    assert 405 == client.patch(url, json={}).status_code
