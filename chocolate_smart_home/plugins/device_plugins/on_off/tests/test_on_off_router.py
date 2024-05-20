from unittest.mock import call, patch

from fastapi.testclient import TestClient

from chocolate_smart_home.main import app


client = TestClient(app)


def test_get_on_off_device(test_data):
    device_id = 1

    resp = client.get("/on_off/{device_id}".format(device_id=device_id))

    assert resp.status_code == 200

    expected_resp_json = {
        "id": 1,
        "on": True,
        "mqtt_id": 111,
        "device_type": {
            "name": "on_off",
            "id": 1,
        },
        "remote_name": "Remote Name 1",
        "name": "Name 1",
        "online": True,
    }

    assert resp.json() == expected_resp_json


def test_delete_on_off_device(test_data):
    device_id = 1

    resp = client.delete(f"/on_off/{device_id}")
    assert resp.status_code == 204

    resp = client.get(f"/on_off/{device_id}")
    assert resp.status_code == 404
    assert resp.json() == {"detail": f"No OnOffDevice with an id of {device_id} found."}


def test_update_single_on_off_device(test_data):
    with patch("chocolate_smart_home.mqtt.client.MQTTClient.publish") as publish:
        resp = client.post("/on_off/1/false")
        publish.assert_called_once_with(topic="/on_off/1/", message="0")

    assert resp.status_code == 204


def test_update_multiple_devices(test_data):
    post_data = {
        "ids": [1, 2],
        "on": False,
    }
    with patch("chocolate_smart_home.mqtt.client.MQTTClient.publish") as publish:
        resp = client.post("/on_off", json=post_data)
        assert publish.call_args_list == [
            call(topic="/on_off/1/", message="0"),
            call(topic="/on_off/2/", message="0"),
        ]

    assert resp.status_code == 204
