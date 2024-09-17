from unittest.mock import call, patch

from fastapi.testclient import TestClient

from chocolate_smart_home.main import app
from chocolate_smart_home.plugins.device_plugins.neo_pixel.schemas import NeoPixelOptions

client = TestClient(app)


def test_get_neo_pixel_devices(populated_test_db):
    resp = client.get("/neo_pixel")
    assert resp.status_code == 200

    expected_resp_json = [
        {
            "id": 1,
            "on": True,
            "twinkle": True,
            "transform": True,
            "ms": 5,
            "brightness": 255,
            "device": {
                "id": 1,
                "client": {
                    "id": 1,
                    "mqtt_id": 123,
                },
                "device_name": {
                    "id": 1,
                    "name": "Test Neo Pixel Device One",
                    "is_server_side_name": False
                },
                "device_type": {
                    "id": 1,
                    "name": "neo_pixel",
                },
                "space": {
                    "id": 1,
                    "name": "Main Space",
                },
                "remote_name": "Test Neo Pixel Device - 1",
                "online": True,
                "reboots": 0,
            },
        },
        {
            "id": 2,
            "on": False,
            "twinkle": True,
            "transform": False,
            "ms": 55,
            "brightness": 123,
            "device": {
                "id": 2,
                "client": {
                    "id": 2,
                    "mqtt_id": 456,
                },
                "device_name": {
                    "id": 2,
                    "name": "Test Neo Pixel Device Two",
                    "is_server_side_name": True
                },
                "device_type": {
                    "id": 1,
                    "name": "neo_pixel",
                },
                "space": None,
                "remote_name": "Test Neo Pixel Device - 2",
                "online": True,
                "reboots": 0,
            },
        },
    ]

    assert resp.json() == expected_resp_json


def test_get_neo_pixel_device(populated_test_db):
    device_id = 1

    resp = client.get("/neo_pixel/{device_id}".format(device_id=device_id))

    assert resp.status_code == 200

    expected_resp_json = {
        "id": 1,
        "on": True,
        "twinkle": True,
        "transform": True,
        "ms": 5,
        "brightness": 255,
        "device": {
            "id": 1,
            "client": {
                "id": 1,
                "mqtt_id": 123,
            },
            "device_name": {
                "id": 1,
                "name": "Test Neo Pixel Device One",
                "is_server_side_name": False
            },
            "device_type": {
                "id": 1,
                "name": "neo_pixel",
            },
            "space": {
                "id": 1,
                "name": "Main Space",
            },
            "remote_name": "Test Neo Pixel Device - 1",
            "online": True,
            "reboots": 0,
        },
    }

    assert resp.json() == expected_resp_json


def test_delete_neo_pixel_device(populated_test_db):
    device_id = 1

    resp = client.delete(f"/neo_pixel/{device_id}")
    assert resp.status_code == 204

    resp = client.get(f"/neo_pixel/{device_id}")
    assert resp.status_code == 404
    assert resp.json() == {"detail": f"No NeoPixel with an id of {device_id} found."}


def test_delete_device_duplicate_deletion_fails(populated_test_db):
    device_id = 1

    resp = client.delete(f"/neo_pixel/{device_id}")
    resp = client.delete(f"/neo_pixel/{device_id}")

    assert resp.status_code == 404
    assert resp.json() == {"detail": f"No NeoPixel with an id of {device_id} found."}


def test_delete_device_fails_on_invalid_device_id(populated_test_db):
    device_id = 777

    resp = client.delete(f"/neo_pixel/{device_id}")

    assert resp.status_code == 404
    assert resp.json() == {"detail": f"No NeoPixel with an id of {device_id} found."}


def test_update_single_neo_pixel_device(populated_test_db):
    with patch("chocolate_smart_home.plugins.device_plugins.neo_pixel.router.publish_message") as publish_message:
        resp = client.post("/neo_pixel/1", json={"on": False})
        publish_message.assert_called_once_with(
            neo_pixel_device_id=1,
            data=NeoPixelOptions(on=False),
        )

    assert resp.status_code == 204

    with patch("chocolate_smart_home.mqtt.client.MQTTClient.publish") as publish:
        resp = client.post("/neo_pixel/1", json={"on": True})
        publish.assert_called_once_with(topic="/neo_pixel/1/", message="on=1;")

    assert resp.status_code == 204


def test_update_multiple_devices(populated_test_db):
    post_data = {"ids":[1, 2], "data":{"on":False, "twinkle":True}}

    with patch("chocolate_smart_home.mqtt.client.MQTTClient.publish") as publish:
        resp = client.post("/neo_pixel", json=post_data)
        assert publish.call_args_list == [
            call(topic="/neo_pixel/1/", message="on=0;twinkle=1;"),
            call(topic="/neo_pixel/2/", message="on=0;twinkle=1;"),
        ]

    assert resp.status_code == 204
