from unittest.mock import call, patch

from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_get_on_off_devices(populated_test_db):
    resp = client.get("/on_off")
    assert resp.status_code == 200

    expected_resp_json = [
        {
            "id": 1,
            "on": True,
            "device": {
                "id": 1,
                "mqtt_id": 123,
                "remote_name": "Test On Device - 1",
                "name": "Test On Device",
                "device_type": {
                    "id": 1,
                    "name": "on_off",
                },
                "tags": [
                    {
                        "id": 1,
                        "name": "Main Tag",
                    },
                ],
                "online": True,
                "reboots": 0,
            },
        },
        {
            "id": 2,
            "on": False,
            "device": {
                "id": 2,
                "mqtt_id": 456,
                "name": "Test Off Device",
                "remote_name": "Test Off Device - 2",
                "device_type": {
                    "id": 1,
                    "name": "on_off",
                },
                "tags": [],
                "online": True,
                "reboots": 0,
            },
        },
    ]

    assert resp.json() == expected_resp_json


def test_get_on_off_device(populated_test_db):
    device_id = 1

    resp = client.get("/on_off/{device_id}".format(device_id=device_id))

    assert resp.status_code == 200

    expected_resp_json = {
        "id": 1,
        "on": True,
        "device": {
            "id": 1,
            "mqtt_id": 123,
            "name": "Test On Device",
            "remote_name": "Test On Device - 1",
            "device_type": {
                "id": 1,
                "name": "on_off",
            },
            "tags": [
                {
                    "id": 1,
                    "name": "Main Tag",
                },
            ],
            "online": True,
            "reboots": 0,
        },
    }

    assert resp.json() == expected_resp_json


def test_delete_on_off_device(populated_test_db):
    device_id = 1

    resp = client.delete(f"/on_off/{device_id}")
    assert resp.status_code == 204

    resp = client.get(f"/on_off/{device_id}")
    assert resp.status_code == 404
    assert resp.json() == {"detail": f"No OnOff with an id of {device_id} found."}


def test_delete_device_duplicate_deletion_fails(populated_test_db):
    device_id = 1

    resp = client.delete(f"/on_off/{device_id}")
    resp = client.delete(f"/on_off/{device_id}")

    assert resp.status_code == 404
    assert resp.json() == {"detail": f"No OnOff with an id of {device_id} found."}


def test_delete_device_fails_on_invalid_device_id(populated_test_db):
    device_id = 777

    resp = client.delete(f"/on_off/{device_id}")

    assert resp.status_code == 404
    assert resp.json() == {"detail": f"No OnOff with an id of {device_id} found."}


def test_update_single_on_off_device(populated_test_db):
    with patch(
        "src.plugins.device_plugins.on_off.router.publish_message"
    ) as publish_message:
        resp = client.post("/on_off/1/false")
        publish_message.assert_called_once_with(on_off_device_id=1, on=False)

    assert resp.status_code == 204

    with patch("src.mqtt.client.MQTTClient.publish") as publish:
        resp = client.post("/on_off/1/false")
        publish.assert_called_once_with(topic="/on_off/1/", message="0")

    assert resp.status_code == 204


def test_update_multiple_devices(populated_test_db):
    post_data = dict(mqtt_ids=[1, 2], on=False)

    with patch("src.mqtt.client.MQTTClient.publish") as publish:
        resp = client.post("/on_off", json=post_data)
        assert publish.call_args_list == [
            call(topic="/on_off/1/", message="0"),
            call(topic="/on_off/2/", message="0"),
        ]

    assert resp.status_code == 204
