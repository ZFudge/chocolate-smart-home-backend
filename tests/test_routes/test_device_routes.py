from unittest.mock import patch

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_route_get_devices_empty(empty_test_db):
    resp = client.get("/devices/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_route_get_devices_returns_devices(populated_test_db):
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
            "plugin": None,
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
            "plugin": None,
        },
    ]


def test_route_get_devices_returns_500_when_raises_exception(populated_test_db):
    with patch(
        "src.routers.devices.crud.get_devices", side_effect=Exception("Test exception")
    ):
        resp = client.get("/devices")
        assert resp.status_code == 500
        assert resp.json() == {
            "detail": "Failed to get devices.",
        }


def test_route_get_device_by_id_returns_500_when_raises_exception(
    populated_test_db,
):
    with patch(
        "src.routers.devices.crud.get_device_by_id",
        side_effect=Exception("Test exception"),
    ):
        resp = client.get("/devices/123")
        assert resp.status_code == 500
        assert resp.json() == {
            "detail": "Failed to get device with mqtt id 123.",
        }


def test_route_get_device_by_id_returns_device(populated_test_db):
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
        "plugin": None,
    }


def test_route_delete_device_deletes_device(populated_test_db):
    resp = client.delete("/devices/123")
    assert resp.status_code == 204
    resp = client.get("/devices/123")
    assert resp.status_code == 200
    assert resp.json() is None


def test_route_delete_device_returns_500_on_subsequent_deletion(populated_test_db):
    resp = client.delete("/devices/123")
    resp = client.delete("/devices/123")
    assert resp.status_code == 500
    assert resp.json() == {
        "detail": (
            "Failed to delete device with mqtt id 123. "
            "No Device object with an mqtt id of 123 found."
        )
    }


def test_route_delete_device_returns_500_on_invalid_mqtt_id(populated_test_db):
    resp = client.delete("/devices/777")
    assert resp.status_code == 500
    assert resp.json() == {
        "detail": (
            "Failed to delete device with mqtt id 777. "
            "No Device object with an mqtt id of 777 found."
        )
    }


def test_route_delete_device_returns_500_when_raises_exception(populated_test_db):
    with patch(
        "src.routers.devices.crud.delete_device",
        side_effect=Exception("Test exception"),
    ):
        resp = client.delete("/devices/123")
        assert resp.status_code == 500
        assert resp.json() == {
            "detail": "Failed to delete device with mqtt id 123.",
        }


def test_route_patch_device_updates_name(populated_test_db):
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
        "plugin": None,
    }
    assert resp.json() == client.get("/devices/123").json()


def test_route_patch_device_updates_tags(populated_test_db):
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
        "plugin": None,
    }
    assert resp.json() == client.get("/devices/123").json()


def test_route_patch_device_updates_both_name_and_tags(populated_test_db):
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
        "plugin": None,
    }
    assert resp.json() == client.get("/devices/123").json()


def test_route_patch_device_returns_500_on_invalid_mqtt_id(populated_test_db):
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


def test_route_patch_device_returns_500_when_raises_exception(populated_test_db):
    with patch(
        "src.routers.devices.crud.patch_device", side_effect=Exception("Test exception")
    ):
        resp = client.patch(
            "/devices", json={"mqtt_id": 123, "name": "Updated Device Name"}
        )
        assert resp.status_code == 500
        assert resp.json() == {
            "detail": "Failed to patch device with mqtt id 123.",
        }


def test_route_patch_device_returns_500_when_none_returned(populated_test_db):
    with patch("src.routers.devices.crud.patch_device", return_value=None):
        resp = client.patch(
            "/devices", json={"mqtt_id": 123, "name": "Updated Device Name"}
        )
        assert resp.status_code == 500
        assert resp.json() == {
            "detail": "Failed to patch device with mqtt id 123.",
        }
