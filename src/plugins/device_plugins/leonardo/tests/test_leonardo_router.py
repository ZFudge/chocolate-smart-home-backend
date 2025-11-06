from unittest.mock import patch

from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_get_leonardo_device(populated_test_db):
    device_id = 1

    resp = client.get("/device/{device_id}".format(device_id=device_id))

    assert resp.status_code == 200

    expected_resp_json = {
        "id": 1,
        "mqtt_id": 123,
        "name": "Test Leonardo Client 1",
        "remote_name": "Test Leonardo Client 1 - 1",
        "device_type": {
            "id": 1,
            "name": "leonardo",
        },
        "tags": [
            {
                "id": 1,
                "name": "Leonardo Client 1 Tag",
            },
        ],
        "online": True,
        "reboots": 0,
    }

    assert resp.json() == expected_resp_json


def test_delete_leonardo_device(populated_test_db):
    device_id = 1

    resp = client.delete(f"/device/{device_id}")
    assert resp.status_code == 204

    resp = client.get(f"/device/{device_id}")
    assert resp.status_code == 404
    assert resp.json() == {"detail": f"No Device with an id of {device_id} found."}


def test_update_leonardo_device(populated_test_db):
    with patch(
        "src.plugins.device_plugins.leonardo.router.publish_message"
    ) as publish_message:
        resp = client.post("/leonardo/1/move")
        publish_message.assert_called_once_with(leonardo_device_id=1, command="move")

    assert resp.status_code == 204


def test_update_leonardo_device_invalid_message(populated_test_db):
    resp = client.post("/leonardo/1/invalid")
    assert resp.status_code == 400
    assert resp.json() == {"detail": "Invalid message: invalid"}
