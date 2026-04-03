from fastapi.testclient import TestClient
import pytest

from src.main import app


client = TestClient(app)


def test_get_devices_data_empty(empty_test_db):
    resp = client.get("/devices/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_device_does_not_exist(empty_test_db):
    resp = client.get("/devices/1")
    assert resp.status_code == 200
    assert resp.json() is None


def test_get_devices_data(populated_test_db):
    resp = client.get("/devices")
    assert resp.status_code == 200

    expected_resp_json = [
        {
            "mqtt_id": 123,
            "remote_name": "Remote Name 1 - 1",
            "name": "Test Device Name 1",
            "reboots": 0,
            "device_type_name": "TEST_DEVICE_TYPE_NAME_1",
            "tags": [1, 2],
        },
        {
            "mqtt_id": 456,
            "remote_name": "Remote Name 2 - 2",
            "name": "Test Device Name 2",
            "reboots": 0,
            "device_type_name": "TEST_DEVICE_TYPE_NAME_2",
            "tags": [],
        },
    ]

    assert resp.json() == expected_resp_json


def test_get_device_data_by_id(populated_test_db):
    resp = client.get("/devices/123")
    assert resp.status_code == 200

    expected_resp_json = {
        "mqtt_id": 123,
        "remote_name": "Remote Name 1 - 1",
        "name": "Test Device Name 1",
        "reboots": 0,
        "device_type_name": "TEST_DEVICE_TYPE_NAME_1",
        "tags": [1, 2],
    }

    assert resp.json() == expected_resp_json


def test_delete_device_request(populated_test_db):
    resp = client.delete("/devices/123")
    assert resp.status_code == 204
    resp = client.get("/devices/123")
    assert resp.status_code == 200
    assert resp.json() is None


def test_delete_device_duplicate_deletion_fails(populated_test_db):
    resp = client.delete("/devices/123")
    resp = client.delete("/devices/123")
    assert resp.status_code == 500
    assert resp.json() == {
        "detail": "Device deletion failed. No Device with an mqtt id of 123 found."
    }


def test_delete_device_fails_on_invalid_device_id(populated_test_db):
    resp = client.delete("/devices/777")
    assert resp.status_code == 500
    assert resp.json() == {
        "detail": "Device deletion failed. No Device with an id of 777 found."
    }


# def test_add_device_tag(populated_test_db):
#     device_id = 123
#     new_tag_id = 2
#     resp = client.put(f"/devices/{device_id}/tags", json={"ids": [new_tag_id]})
#     assert resp.status_code == 200

#     expected_data = {
#         "mqtt_id": 123,
#         "remote_name": "Remote Name 1 - 1",
#         "name": "Test Device Name 1",
#         "reboots": 0,
#         "device_type_name": "TEST_DEVICE_TYPE_NAME_1",
#         "tags": [2],
#     }

#     assert resp.json() == expected_data


# def test_request_controllers_state():
#     resp = client.head("/devices/broadcast_request_devices_state/")
#     assert resp.status_code == 204


# def test_update_device_name(populated_test_db):
#     resp = client.post("/devices/123/name", json={"name": "Updated Device Name"})
#     assert resp.status_code == 200
#     expected_data = {
#         "device_type_name": "TEST_DEVICE_TYPE_NAME_1",
#         "mqtt_id": 123,
#         "name": "Updated Device Name",
#         "reboots": 0,
#         "remote_name": "Remote Name 1 - 1",
#         "tags": [1, 2],
#     }
#     assert resp.json() == expected_data

# @pytest.mark.asyncio
# async def test_update_device_name_fail(populated_test_db):
#     resp = client.post("/devices/777/name", json={"name": "Updated Device Name"})
#     assert resp.status_code == 500
#     assert resp.json() == {
#         "detail": "Failed to update device name for Device with mqtt id of 777 - Device with mqtt id 777 not found"
#     }
