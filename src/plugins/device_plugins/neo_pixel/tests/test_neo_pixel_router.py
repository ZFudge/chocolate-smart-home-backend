from unittest.mock import call, patch

from fastapi.testclient import TestClient

from src.main import app
from src.plugins.device_plugins.neo_pixel.schemas import (
    NeoPixelOptions,
)


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
            "all_twinkle_colors_are_current": None,
            "scheduled_palette_rotation": None,
            "ms": 5,
            "brightness": 255,
            "palette": [
                "#000102",
                "#030405",
                "#060708",
                "#090a0b",
                "#0c0d0e",
                "#0f1011",
                "#121314",
                "#d2dce6",
                "#f0faff",
            ],
            "pir": {
                "armed": True,
                "timeout": 172,
            },
            "device": {
                "id": 1,
                "mqtt_id": 123,
                "name": "Test Neo Pixel Device One",
                "device_type": {
                    "id": 1,
                    "name": "neo_pixel",
                },
                "tags": [
                    {
                        "id": 1,
                        "name": "NeoPixel Tag",
                    },
                ],
                "remote_name": "Test Neo Pixel Device - 1",
                "online": True,
                "reboots": 0,
            },
        },
        {
            "id": 2,
            "on": False,
            "twinkle": True,
            "all_twinkle_colors_are_current": None,
            "scheduled_palette_rotation": None,
            "transform": False,
            "ms": 55,
            "brightness": 123,
            "palette": [
                "#000102",
                "#030405",
                "#060708",
                "#090a0b",
                "#0c0d0e",
                "#0f1011",
                "#121314",
                "#d2dce6",
                "#f0faff",
            ],
            "pir": None,
            "device": {
                "id": 2,
                "mqtt_id": 456,
                "name": "Test Neo Pixel Device Two",
                "device_type": {
                    "id": 1,
                    "name": "neo_pixel",
                },
                "tags": [],
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
        "all_twinkle_colors_are_current": None,
        "scheduled_palette_rotation": None,
        "transform": True,
        "ms": 5,
        "brightness": 255,
        "palette": [
            "#000102",
            "#030405",
            "#060708",
            "#090a0b",
            "#0c0d0e",
            "#0f1011",
            "#121314",
            "#d2dce6",
            "#f0faff",
        ],
        "pir": {
            "armed": True,
            "timeout": 172,
        },
        "device": {
            "id": 1,
            "mqtt_id": 123,
            "name": "Test Neo Pixel Device One",
            "remote_name": "Test Neo Pixel Device - 1",
            "online": True,
            "reboots": 0,
            "device_type": {
                "id": 1,
                "name": "neo_pixel",
            },
            "tags": [
                {
                    "id": 1,
                    "name": "NeoPixel Tag",
                },
            ],
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

    with patch(
        "src.plugins.device_plugins.neo_pixel.router.publish_message"
    ) as publish_message:
        resp = client.post("/neo_pixel/1", json=post_data)
        publish_message.assert_called_once_with(
            neo_pixel_device_id=1, data=expected_params
        )

    assert resp.status_code == 204


def test_update_single_neo_pixel_device_outgoing_msg(populated_test_db):
    post_data = dict(on=True, twinkle=False, transform=True, ms=154, brightness=88)
    expected_out_msg = "on=1;twinkle=0;transform=1;ms=154;brightness=88;"
    with patch("src.mqtt.client.MQTTClient.publish") as publish:
        resp = client.post("/neo_pixel/1", json=post_data)
        publish.assert_called_once_with(topic="/neo_pixel/1/", message=expected_out_msg)

    assert resp.status_code == 204


def test_update_multiple_devices(populated_test_db):
    post_data = dict(mqtt_ids=[1, 2], data=dict(on=False, twinkle=True, ms=201))
    expected_msg = "on=0;twinkle=1;ms=201;"

    with patch("src.mqtt.client.MQTTClient.publish") as publish:
        resp = client.post("/neo_pixel", json=post_data)
        assert publish.call_args_list == [
            call(topic="/neo_pixel/1/", message=expected_msg),
            call(topic="/neo_pixel/2/", message=expected_msg),
        ]

    assert resp.status_code == 204


def test_update_neo_pixel_device_name(populated_test_db):
    resp = client.post("/device/123/name", json={"name": "Updated Neo Pixel Device Name"})
    assert resp.status_code == 200
    expected_data = {
        'device_type': {
            'id': 1,
            'name': 'neo_pixel',
        },
        'id': 1,
        'mqtt_id': 123,
        'name': 'Updated Neo Pixel Device Name',
        'online': True,
        'reboots': 0,
        'remote_name': 'Test Neo Pixel Device - 1',
        'tags': [
            {
                'id': 1,
                'name': 'NeoPixel Tag',
            },
        ],
    }
    assert resp.json() == expected_data


def test_update_neo_pixel_device_name_fail(populated_test_db):
    resp = client.post("/device/777/name", json={"name": "Updated Neo Pixel Device Name"})
    assert resp.status_code == 500
    assert resp.json() == {"detail": "Failed to update device name for Device with mqtt id of 777 - No row was found when one was required"}


def test_get_palettes_route(populated_test_db):
    resp = client.get("/neo_pixel/palettes/")
    assert resp.status_code == 200
    data = resp.json()
    assert data == [
        {
            'id': 1,
            'name': 'Test Palette',
            'colors': ['#000102', '#030405', '#060708', '#090a0b', '#0c0d0e', '#0f1011', '#121314', '#151617', '#18191a'],
        }
    ]


def test_create_palette(empty_test_db):
    post_data = {
        "name": "Test Palette",
        "colors": ["#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000"]
    }
    resp = client.post("/neo_pixel/palettes/", json=post_data)
    assert resp.status_code == 200
    expected_data = {
        "id": 1,
        "name": "Test Palette",
        "colors": ["#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000"]
    }
    assert resp.json() == expected_data


def test_create_palette_duplicate(populated_test_db):
    post_data = {
        "name": "Test Palette",
        "colors": ["#000102", "#030405", "#060708", "#090a0b", "#0c0d0e", "#0f1011", "#121314", "#151617", "#18191a"]
    }
    resp = client.post("/neo_pixel/palettes/", json=post_data)
    assert resp.status_code == 500
    assert resp.json() == {"detail": "Palette with name Test Palette already exists"}
