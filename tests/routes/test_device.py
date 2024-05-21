from fastapi.testclient import TestClient

from chocolate_smart_home.main import app


client = TestClient(app)


def test_create_device(test_database):
    resp = client.post(
        "/create_device/",
        json={
            "mqtt_id": 0,
            "device_type_name": "test_device_type_name",
            "remote_name": "Test Device - 123",
            "name": "",
        },
    )

    assert resp.status_code == 200

    data = resp.json()
    assert data["mqtt_id"] == 0
    assert data["device_type"]["name"] == "test_device_type_name"
    assert data["remote_name"] == "Test Device - 123"
    assert data["name"] == ""


def test_create_device_used_mqtt_id_fails(test_database):
    resp = client.post(
        "/create_device/",
        json={
            "mqtt_id": 0,
            "device_type_name": "test_device_type_name_1",
            "remote_name": "Test Device - 1",
            "name": "This Name",
        }
    )
    resp = client.post(
        "/create_device/",
        json={
            "mqtt_id": 0,
            "device_type_name": "test_device_type_name_2",
            "remote_name": "Test Device - 2",
            "name": "Other Name",
        }
    )

    assert resp.status_code == 500
    assert resp.json() == { "detail": "Key (mqtt_id)=(0) already exists." }


def test_create_device_methods_not_allowed(test_database):
    url = "/create_device/"
    assert 405 == client.get(url).status_code
    assert 405 == client.delete(url).status_code
    assert 405 == client.patch(url, json={}).status_code


def test_get_devices_data_empty(test_database):
    resp = client.get("/get_devices_data/")

    data = resp.json()
    assert data == []


def test_get_devices_data(test_data):
    resp = client.get("/get_devices_data/")

    assert resp.status_code == 200

    expected_resp_json = [
        {
            "mqtt_id": 111,
            "device_type": {
                "name": "TEST_DEVICE_TYPE_NAME_1",
                "id": 1,
            },
            "remote_name": "Remote Name 1",
            "name": "Name 1",
            "online": True,
            "id": 1,
        }, {
            "mqtt_id": 222,
            "device_type": {
                "name": "TEST_DEVICE_TYPE_NAME_2",
                "id": 2,
            },
            "remote_name": "Remote Name 2",
            "name": "Name 2",
            "online": False,
            "id": 2,
        },
    ]

    assert resp.json() == expected_resp_json


def test_get_device_data(test_data):
    resp = client.get("/get_device_data/{device_id}".format(device_id=1))

    assert resp.status_code == 200

    expected_resp_json = {
        "mqtt_id": 111,
        "device_type": {
            "name": "TEST_DEVICE_TYPE_NAME_1",
            "id": 1
        },
        "remote_name": "Remote Name 1",
        "name": "Name 1",
        "online": True,
        "id": 1,
    }

    assert resp.json() == expected_resp_json


def test_delete_device_request(test_data):
    device_id = 1

    resp = client.delete(f"/delete_device/{device_id}")
    assert resp.status_code == 204

    resp = client.get(f"/get_device_data/{device_id}")
    assert resp.status_code == 404
    assert resp.json() == {"detail": f"No device with an id of {device_id} found."}


def test_delete_device_duplicate_deletion_fails(test_data):
    device_id = 1

    resp = client.delete(f"/delete_device/{device_id}")
    resp = client.delete(f"/delete_device/{device_id}")

    assert resp.status_code == 500
    assert resp.json() == {"detail": f"Device deletion failed. No Device with an id of {device_id} found."}


def test_delete_device_fails_on_invalid_device_id(test_data):
    device_id = 777

    resp = client.delete(f"/delete_device/{device_id}")

    assert resp.status_code == 500
    assert resp.json() == {"detail": f"Device deletion failed. No Device with an id of {device_id} found."}
