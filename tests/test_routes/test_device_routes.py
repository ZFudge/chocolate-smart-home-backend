from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_empty_get_devices(empty_test_db):
    resp = client.get("/devices/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_nonexistent_get_device(empty_test_db):
    resp = client.get("/devices/1")
    assert resp.status_code == 200
    assert resp.json() is None


def test_get_devices(populated_test_db):
    resp = client.get("/devices")
    assert resp.status_code == 200
    assert resp.json() == [
        {
            "mqtt_id": 123,
            "remote_name": "Remote Name 1 - 1",
            "name": "Test Device Name 1",
            "reboots": 0,
            "device_type_name": "TEST_DEVICE_TYPE_NAME_1",
            "tags": [1, 2],
            "last_seen": "2025-01-02 00:00:00",
            "last_update_sent": "2025-01-01 00:00:00",
        },
        {
            "mqtt_id": 234,
            "remote_name": "Remote Name 2 - 2",
            "name": "Test Device Name 2",
            "reboots": 0,
            "device_type_name": "TEST_DEVICE_TYPE_NAME_2",
            "tags": None,
            "last_seen": "2025-01-01 00:00:00",
            "last_update_sent": "2025-01-02 00:00:00",
        },
    ]


def test_get_device_data_by_id(populated_test_db):
    resp = client.get("/devices/123")
    assert resp.status_code == 200
    assert resp.json() == {
        "mqtt_id": 123,
        "remote_name": "Remote Name 1 - 1",
        "name": "Test Device Name 1",
        "reboots": 0,
        "device_type_name": "TEST_DEVICE_TYPE_NAME_1",
        "tags": [1, 2],
        "last_seen": "2025-01-02 00:00:00",
        "last_update_sent": "2025-01-01 00:00:00",
    }


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
        "detail": (
            "Failed to delete device with mqtt id 123. "
            "No Device object with an mqtt id of 123 found."
        )
    }


def test_delete_device_fails_on_invalid_device_id(populated_test_db):
    resp = client.delete("/devices/777")
    assert resp.status_code == 500
    assert resp.json() == {
        "detail": (
            "Failed to delete device with mqtt id 777. "
            "No Device object with an mqtt id of 777 found."
        )
    }


def test_patch_device_name_request(populated_test_db):
    resp = client.patch(
        "/devices",
        json={
            "mqtt_id": 123,
            "name": "Updated Device Name",
        },
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "mqtt_id": 123,
        "remote_name": "Remote Name 1 - 1",
        "name": "Updated Device Name",
        "reboots": 0,
        "device_type_name": "TEST_DEVICE_TYPE_NAME_1",
        "tags": [1, 2],
        "last_seen": "2025-01-02 00:00:00",
        "last_update_sent": "2025-01-01 00:00:00",
    }
    assert resp.json() == client.get("/devices/123").json()


def test_patch_device_tags_request(populated_test_db):
    resp = client.patch(
        "/devices",
        json={
            "mqtt_id": 123,
            "tags": [3],
        },
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "mqtt_id": 123,
        "remote_name": "Remote Name 1 - 1",
        "name": "Test Device Name 1",
        "reboots": 0,
        "device_type_name": "TEST_DEVICE_TYPE_NAME_1",
        "tags": [3],
        "last_seen": "2025-01-02 00:00:00",
        "last_update_sent": "2025-01-01 00:00:00",
    }
    assert resp.json() == client.get("/devices/123").json()


def test_patch_both_name_and_tags_request(populated_test_db):
    resp = client.patch(
        "/devices",
        json={
            "mqtt_id": 123,
            "tags": [3],
            "name": "Updated Device Name",
        },
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "mqtt_id": 123,
        "remote_name": "Remote Name 1 - 1",
        "name": "Updated Device Name",
        "reboots": 0,
        "device_type_name": "TEST_DEVICE_TYPE_NAME_1",
        "tags": [3],
        "last_seen": "2025-01-02 00:00:00",
        "last_update_sent": "2025-01-01 00:00:00",
    }
    assert resp.json() == client.get("/devices/123").json()


def test_patch_device_fails_on_invalid_device_id(populated_test_db):
    resp = client.patch(
        "/devices",
        json={
            "mqtt_id": 777,
            "tags": [3],
            "name": "Updated Device Name",
        },
    )
    assert resp.status_code == 500
    assert resp.json() == {
        "detail": (
            "Failed to patch device with mqtt id 777. "
            "No Device object with an mqtt id of 777 found."
        )
    }
