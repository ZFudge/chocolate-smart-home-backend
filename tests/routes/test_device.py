from fastapi.testclient import TestClient

from chocolate_smart_home.main import app


client = TestClient(app)


def test_get_devices_data_empty(empty_test_db):
    resp = client.get("/device")
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_devices_data(populated_test_db):
    resp = client.get("/device")
    assert resp.status_code == 200

    expected_resp_json = [
        {
            "id": 1,
            "client": {
                "id": 1,
                "mqtt_id": 123,
            },
            "device_name": {
                "id": 1,
                "name": "Test Device Name 1",
                "is_server_side_name": False,
            },
            "device_type": {
                "id": 1,
                "name": "TEST_DEVICE_TYPE_NAME_1",
            },
            "space": {
                "id": 1,
                "name": "Main Space",
            },
            "remote_name": "Remote Name 1 - 1",
            "online": True,
            "reboots": 0,
        },
        {
            "id": 2,
            "client": {
                "id": 2,
                "mqtt_id": 456,
            },
            "device_name": {
                "id": 2,
                "name": "Test Device Name 2",
                "is_server_side_name": True,
            },
            "device_type": {
                "name": "TEST_DEVICE_TYPE_NAME_2",
                "id": 2,
            },
            "space": {},
            "remote_name": "Remote Name 2 - 2",
            "online": False,
            "reboots": 0,
        },
    ]

    assert resp.json() == expected_resp_json


def test_get_device_data(populated_test_db):
    resp = client.get("/device/{device_id}".format(device_id=1))
    assert resp.status_code == 200

    expected_resp_json = {
        "id": 1,
        "client": {
            "id": 1,
            "mqtt_id": 123,
        },
        "device_type": {
            "id": 1,
            "name": "TEST_DEVICE_TYPE_NAME_1",
        },
        "device_name": {
            "id": 1,
            "name": "Test Device Name 1",
            "is_server_side_name": False,
        },
        "space": {
            "id": 1,
            "name": "Main Space",
        },
        "remote_name": "Remote Name 1 - 1",
        "online": True,
        "reboots": 0,
    }

    assert resp.json() == expected_resp_json


def test_delete_device_request(populated_test_db):
    device_id = 1
    resp = client.delete(f"/device/{device_id}")
    assert resp.status_code == 204
    resp = client.get(f"/device/{device_id}")
    assert resp.status_code == 404
    assert resp.json() == {"detail": f"No Device with an id of {device_id} found."}


def test_delete_device_duplicate_deletion_fails(populated_test_db):
    device_id = 1
    resp = client.delete(f"/device/{device_id}")
    resp = client.delete(f"/device/{device_id}")
    assert resp.status_code == 500
    assert resp.json() == {
        "detail": f"Device deletion failed. No Device with an id of {device_id} found."
    }


def test_delete_device_fails_on_invalid_device_id(populated_test_db):
    device_id = 777
    resp = client.delete(f"/device/{device_id}")
    assert resp.status_code == 500
    assert resp.json() == {
        "detail": f"Device deletion failed. No Device with an id of {device_id} found."
    }


def test_add_device_space(populated_test_db):
    device_id = 1
    new_space_id = 2
    resp = client.post(f"/device/space/{device_id}", json={"id": new_space_id})
    assert resp.status_code == 200

    expected_data = {
        'id': 1,
        'client': {
            'id': 1,
            'mqtt_id': 123,
        },
        'device_name': {
            'id': 1,
            'is_server_side_name': False,
            'name': 'Test Device Name 1',
        },
        'device_type': {
            'id': 1,
            'name': 'TEST_DEVICE_TYPE_NAME_1',
        },
        'space': {
            'id': 2,
            'name': 'Other Space',
        },
        'online': True,
        'reboots': 0,
        'remote_name': 'Remote Name 1 - 1',
    }

    assert resp.json() == expected_data
