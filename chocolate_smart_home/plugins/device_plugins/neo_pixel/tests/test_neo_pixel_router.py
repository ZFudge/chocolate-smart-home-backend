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
            "palette": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26],
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
            "palette": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26],
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
        "palette": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26],
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


def test_update_single_neo_pixel_device_publish(populated_test_db):
    post_data = dict(on=False, twinkle=True, transform=False, ms=77, brightness=44)
    expected_params = NeoPixelOptions(**post_data)

    with patch("chocolate_smart_home.plugins.device_plugins.neo_pixel.router.publish_message") as publish_message:
        resp = client.post("/neo_pixel/1", json=post_data)
        publish_message.assert_called_once_with(neo_pixel_device_id=1, data=expected_params)

    assert resp.status_code == 204


def test_update_single_neo_pixel_device_outgoing_msg(populated_test_db):
    post_data = dict(on=True, twinkle=False, transform=True, ms=154, brightness=88)
    expected_out_msg = "on=1;twinkle=0;transform=1;ms=154;brightness=88;"
    with patch("chocolate_smart_home.mqtt.client.MQTTClient.publish") as publish:
        resp = client.post("/neo_pixel/1", json=post_data)
        publish.assert_called_once_with(topic="/neo_pixel/1/", message=expected_out_msg)

    assert resp.status_code == 204


def test_update_multiple_devices(populated_test_db):
    post_data = dict(ids=[1, 2], data=dict(on=False, twinkle=True, ms=201))
    expected_msg = "on=0;twinkle=1;ms=201;"

    with patch("chocolate_smart_home.mqtt.client.MQTTClient.publish") as publish:
        resp = client.post("/neo_pixel", json=post_data)
        assert publish.call_args_list == [
            call(topic="/neo_pixel/1/", message=expected_msg),
            call(topic="/neo_pixel/2/", message=expected_msg),
        ]

    assert resp.status_code == 204
