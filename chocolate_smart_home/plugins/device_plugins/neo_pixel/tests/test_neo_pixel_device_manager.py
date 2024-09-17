import pytest
from sqlalchemy.exc import NoResultFound

from chocolate_smart_home.plugins.device_plugins.neo_pixel.device_manager import (
    NeoPixelDeviceManager,
)


def test_device_manager_create(empty_test_db):
    device_data = {
        "on": True,
        "twinkle": True,
        "transform": True,
        "ms": 5,
        "brightness": 255,
        "mqtt_id": 123,
        "device_type_name": "neo_pixel",
        "remote_name": "Neo Pixel Device - 1",
    }
    neo_pixel_device = NeoPixelDeviceManager().create_device(device_data)
    assert neo_pixel_device.id == 1
    assert neo_pixel_device.on is True
    assert neo_pixel_device.twinkle is True
    assert neo_pixel_device.transform is True
    assert neo_pixel_device.ms == 5
    assert neo_pixel_device.brightness == 255
    assert neo_pixel_device.device.remote_name == "Neo Pixel Device - 1"
    assert neo_pixel_device.device.client.mqtt_id == 123
    assert neo_pixel_device.device.device_type.name == "neo_pixel"


def test_device_manager_create_fails_missing_keys(empty_test_db):
    with pytest.raises(KeyError, match="on"):
        NeoPixelDeviceManager().create_device(
            {
                "mqtt_id": 123,
                "device_type_name": "neo_pixel",
                "remote_name": "Neo Pixel Device - 1",
            }
        )


def test_device_manager_update(populated_test_db):
    device_data = {
        "on": True,
        "twinkle": True,
        "transform": True,
        "ms": 5,
        "brightness": 255,
        "mqtt_id": 123,
        "device_type_name": "neo_pixel",
        "remote_name": "Neo Pixel Device - 1",
    }
    neo_pixel_device = NeoPixelDeviceManager().update_device(device_data)

    assert neo_pixel_device.id == 1
    assert neo_pixel_device.on is True
    assert neo_pixel_device.twinkle is True
    assert neo_pixel_device.transform is True
    assert neo_pixel_device.ms == 5
    assert neo_pixel_device.brightness == 255
    assert neo_pixel_device.device.remote_name == "Neo Pixel Device - 1"
    assert neo_pixel_device.device.client.mqtt_id == 123
    assert neo_pixel_device.device.device_type.name == "neo_pixel"


def test_device_manager_update_fails_device_does_not_exist(empty_test_db):
    device_data = {
        "on": True,
        "mqtt_id": 123,
        "device_type_name": "neo_pixel",
        "remote_name": "Neo Pixel Device - 1",
    }
    with pytest.raises(NoResultFound):
        NeoPixelDeviceManager().update_device(device_data)


def test_device_manager_update_fails_missing_keys(populated_test_db):
    with pytest.raises(KeyError, match="on"):
        NeoPixelDeviceManager().update_device(
            {
                "twinkle": True,
                "transform": True,
                "ms": 5,
                "brightness": 255,
                "mqtt_id": 123,
                "device_type_name": "neo_pixel",
                "remote_name": "Neo Pixel Device - 1",
            }
        )
    with pytest.raises(KeyError, match="mqtt_id"):
        NeoPixelDeviceManager().update_device(
            {
                "on": True,
                "twinkle": True,
                "transform": True,
                "ms": 5,
                "brightness": 255,
                "device_type_name": "neo_pixel",
                "remote_name": "Neo Pixel Device - 1",
            }
        )
    with pytest.raises(KeyError, match="device_type_name"):
        NeoPixelDeviceManager().update_device(
            {
                "on": True,
                "twinkle": True,
                "transform": True,
                "ms": 5,
                "brightness": 255,
                "mqtt_id": 123,
                "remote_name": "Neo Pixel Device - 1",
            }
        )
    with pytest.raises(KeyError, match="remote_name"):
        NeoPixelDeviceManager().update_device(
            {
                "on": True,
                "twinkle": True,
                "transform": True,
                "ms": 5,
                "brightness": 255,
                "mqtt_id": 123,
                "device_type_name": "neo_pixel",
            }
        )
