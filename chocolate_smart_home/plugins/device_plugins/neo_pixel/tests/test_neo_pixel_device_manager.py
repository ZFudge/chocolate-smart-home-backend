import pytest
from sqlalchemy.exc import NoResultFound

from chocolate_smart_home.plugins.device_plugins.neo_pixel.device_manager import (
    NeoPixelDeviceManager,
)
from chocolate_smart_home.plugins.device_plugins.neo_pixel.schemas import (
    DeviceReceived,
    NeoPixelDeviceReceived,
    PIR,
)


def test_device_manager_create(empty_test_db):
    device_data = NeoPixelDeviceReceived(
        on=True,
        twinkle=True,
        transform=True,
        ms=5,
        brightness=255,
        palette=[
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ],
        pir=PIR(armed=True, timeout_seconds=65),
        device=DeviceReceived(
            mqtt_id=123,
            device_type_name="neo_pixel",
            remote_name="Neo Pixel Device - 1",
        ),
    )
    neo_pixel_device = NeoPixelDeviceManager().create_device(device_data)
    assert neo_pixel_device.id == 1
    assert neo_pixel_device.on is True
    assert neo_pixel_device.twinkle is True
    assert neo_pixel_device.transform is True
    assert neo_pixel_device.ms == 5
    assert neo_pixel_device.brightness == 255
    assert neo_pixel_device.pir_armed is True
    assert neo_pixel_device.pir_timeout_seconds == 65
    assert neo_pixel_device.palette == [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
    ]
    assert neo_pixel_device.device.remote_name == "Neo Pixel Device - 1"
    assert neo_pixel_device.device.mqtt_id == 123
    assert neo_pixel_device.device.device_type.name == "neo_pixel"


def test_device_manager_update(populated_test_db):
    device_data = NeoPixelDeviceReceived(
        on=True,
        twinkle=True,
        transform=True,
        ms=5,
        brightness=255,
        palette=[
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ],
        pir=PIR(armed=False, timeout_seconds=20),
        device=DeviceReceived(
            mqtt_id=123,
            device_type_name="neo_pixel",
            remote_name="Neo Pixel Device - 1",
        ),
    )
    neo_pixel_device = NeoPixelDeviceManager().update_device(device_data)

    assert neo_pixel_device.id == 1
    assert neo_pixel_device.on is True
    assert neo_pixel_device.twinkle is True
    assert neo_pixel_device.transform is True
    assert neo_pixel_device.ms == 5
    assert neo_pixel_device.brightness == 255
    assert neo_pixel_device.pir_armed is False
    assert neo_pixel_device.pir_timeout_seconds == 20
    assert neo_pixel_device.palette == [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
    ]
    assert neo_pixel_device.device.remote_name == "Neo Pixel Device - 1"
    assert neo_pixel_device.device.mqtt_id == 123
    assert neo_pixel_device.device.device_type.name == "neo_pixel"


def test_device_manager_update_fails_device_does_not_exist(empty_test_db):
    device_data = NeoPixelDeviceReceived(
        on=True,
        twinkle=True,
        transform=True,
        ms=5,
        brightness=255,
        palette=[
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ],
        pir=None,
        device=DeviceReceived(
            mqtt_id=123,
            device_type_name="neo_pixel",
            remote_name="Neo Pixel Device - 1",
        ),
    )
    with pytest.raises(NoResultFound):
        NeoPixelDeviceManager().update_device(device_data)
