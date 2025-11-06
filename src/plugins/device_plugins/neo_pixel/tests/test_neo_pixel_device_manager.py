import pytest
from sqlalchemy.exc import NoResultFound

from src.plugins.device_plugins.neo_pixel.device_manager import (
    NeoPixelDeviceManager,
)
from src.plugins.device_plugins.neo_pixel.schemas import (
    DeviceReceived,
    NeoPixelDeviceReceived,
    PIR,
)
from src.schemas.websocket_msg import WebsocketMessage


def test_device_manager_create(empty_test_db):
    device_data = NeoPixelDeviceReceived(
        on=True,
        twinkle=True,
        transform=True,
        ms=5,
        brightness=255,
        palette=[
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
        pir=PIR(armed=True, timeout=65),
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
    assert neo_pixel_device.armed is True
    assert neo_pixel_device.timeout == 65
    assert neo_pixel_device.palette == [
        "#000102",
        "#030405",
        "#060708",
        "#090a0b",
        "#0c0d0e",
        "#0f1011",
        "#121314",
        "#d2dce6",
        "#f0faff",
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
        pir=PIR(armed=False, timeout=20),
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
    assert neo_pixel_device.armed is False
    assert neo_pixel_device.timeout == 20
    assert neo_pixel_device.palette == [
        "#000102",
        "#030405",
        "#060708",
        "#090a0b",
        "#0c0d0e",
        "#0f1011",
        "#121314",
        "#d2dce6",
        "#f0faff",
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
        pir=None,
        device=DeviceReceived(
            mqtt_id=123,
            device_type_name="neo_pixel",
            remote_name="Neo Pixel Device - 1",
        ),
    )
    with pytest.raises(NoResultFound):
        NeoPixelDeviceManager().update_device(device_data)


def test_device_manager__scheduled_palette_rotation(populated_test_db):
    assert (
        NeoPixelDeviceManager().get_devices_by_mqtt_id(123).scheduled_palette_rotation
        is True
    )

    NeoPixelDeviceManager().update_server_side_values(
        WebsocketMessage(
            device_type_name="neo_pixel",
            mqtt_ids=[123],
            name="scheduled_palette_rotation",
            value=False,
        )
    )

    assert (
        NeoPixelDeviceManager().get_devices_by_mqtt_id(123).scheduled_palette_rotation
        is False
    )


def test_device_manager__scheduled_palette_rotation_multiple_devices(populated_test_db):
    assert (
        NeoPixelDeviceManager().get_devices_by_mqtt_id(123).scheduled_palette_rotation
        is True
    )
    assert (
        NeoPixelDeviceManager().get_devices_by_mqtt_id(456).scheduled_palette_rotation
        is None
    )

    NeoPixelDeviceManager().update_server_side_values(
        WebsocketMessage(
            device_type_name="neo_pixel",
            mqtt_ids=[123, 456],
            name="scheduled_palette_rotation",
            value=True,
        )
    )

    assert (
        NeoPixelDeviceManager().get_devices_by_mqtt_id(123).scheduled_palette_rotation
        is True
    )
    assert (
        NeoPixelDeviceManager().get_devices_by_mqtt_id(456).scheduled_palette_rotation
        is True
    )

    NeoPixelDeviceManager().update_server_side_values(
        WebsocketMessage(
            device_type_name="neo_pixel",
            mqtt_ids=[123, 456],
            name="scheduled_palette_rotation",
            value=False,
        )
    )

    assert (
        NeoPixelDeviceManager().get_devices_by_mqtt_id(123).scheduled_palette_rotation
        is False
    )
    assert (
        NeoPixelDeviceManager().get_devices_by_mqtt_id(456).scheduled_palette_rotation
        is False
    )
