from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from chocolate_smart_home.main import app
import chocolate_smart_home.schemas as schemas


client = TestClient(app)


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


def test_create_device_methods_not_allowed(test_database):
    url = "/create_device/"
    assert 405 == client.get(url).status_code
    assert 405 == client.delete(url).status_code
    assert 405 == client.patch(url, json={}).status_code



def test_get_devices_data_empty(test_database):
    response = client.get("/get_devices_data/")

    data = response.json()
    assert data == []


def test_get_devices_data(test_data):
    response = client.get("/get_devices_data/")

    assert response.status_code == 200

    expected_response_json = [
        {
            'mqtt_id': 111,
            'device_type': {
                'name': 'TEST_DEVICE_TYPE_NAME_1',
                'id': 1
            },
            'remote_name': 'Remote Name 1',
            'name': 'Name 1',
            'online': True,
            'id': 1
        }, {
            'mqtt_id': 222,
            'device_type': {
                'name': 'TEST_DEVICE_TYPE_NAME_2',
                'id': 2
            },
            'remote_name': 'Remote Name 2',
            'name': 'Name 2',
            'online': False,
            'id': 2
        }
    ]

    assert response.json() == expected_response_json


def test_get_device_data(test_data):
    response = client.get("/get_device_data/{device_id}".format(device_id=1))

    assert response.status_code == 200

    expected_response_json = {
        'mqtt_id': 111,
        'device_type': {
            'name': 'TEST_DEVICE_TYPE_NAME_1',
            'id': 1
        },
        'remote_name': 'Remote Name 1',
        'name': 'Name 1',
        'online': True,
        'id': 1
    }

    assert response.json() == expected_response_json


def test_delete_device_request(test_data):
    device_id = 1
    response = client.delete(f"/delete_device/{device_id}")

    assert response.status_code == 204

    response = client.get(f"/get_device_data/{device_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": f"No device found with an id of {device_id}"}


def test_delete_device_fails_on_invalid_device_id(test_data):
    device_id = 777
    response = client.delete(f"/delete_device/{device_id}")

    assert response.status_code == 500
    assert response.json() == {"detail": f"No device found with an id of {device_id}"}
