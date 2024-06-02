from fastapi.testclient import TestClient

from chocolate_smart_home.main import app


client = TestClient(app)


def test_get_devices_data_empty(empty_test_db):
    resp = client.get("/get_devices_data/")

    data = resp.json()
    assert data == []


def test_get_devices_data(populated_test_db):
    resp = client.get("/get_devices_data/")

    assert resp.status_code == 200

    expected_resp_json = [
        {
            "mqtt_id": 123,
            "device_type": {
                "name": "TEST_DEVICE_TYPE_NAME_1",
                "id": 1,
            },
            "remote_name": "Remote Name 1",
            "device_name": "Test Device Name 1",
            "online": True,
            "id": 1,
        },
        {
            "mqtt_id": 456,
            "device_type": {
                "name": "TEST_DEVICE_TYPE_NAME_2",
                "id": 2,
            },
            "remote_name": "Remote Name 2",
            "device_name": "Test Device Name 2",
            "online": False,
            "id": 2,
        },
    ]

    assert resp.json() == expected_resp_json


def test_get_device_data(populated_test_db):
    resp = client.get("/get_device_data/{device_id}".format(device_id=1))

    assert resp.status_code == 200

    expected_resp_json = {
        "mqtt_id": 123,
        "device_type": {"name": "TEST_DEVICE_TYPE_NAME_1", "id": 1},
        "remote_name": "Remote Name 1",
        "device_name": "Test Device Name 1",
        "online": True,
        "id": 1,
    }

    assert resp.json() == expected_resp_json


def test_delete_device_request(populated_test_db):
    device_id = 1

    resp = client.delete(f"/delete_device/{device_id}")
    assert resp.status_code == 204

    resp = client.get(f"/get_device_data/{device_id}")
    assert resp.status_code == 404
    assert resp.json() == {"detail": f"No device with an id of {device_id} found."}


def test_delete_device_duplicate_deletion_fails(populated_test_db):
    device_id = 1

    resp = client.delete(f"/delete_device/{device_id}")
    resp = client.delete(f"/delete_device/{device_id}")

    assert resp.status_code == 500
    assert resp.json() == {
        "detail": f"Device deletion failed. No Device with an id of {device_id} found."
    }


def test_delete_device_fails_on_invalid_device_id(populated_test_db):
    device_id = 777

    resp = client.delete(f"/delete_device/{device_id}")

    assert resp.status_code == 500
    assert resp.json() == {
        "detail": f"Device deletion failed. No Device with an id of {device_id} found."
    }
