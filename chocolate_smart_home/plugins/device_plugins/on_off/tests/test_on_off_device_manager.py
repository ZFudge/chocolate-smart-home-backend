import pytest
from sqlalchemy.exc import NoResultFound

from chocolate_smart_home.plugins.device_plugins.on_off.device_manager import (
    OnOffDeviceManager,
)
from chocolate_smart_home.plugins.device_plugins.on_off.schemas import (
    OnOffDeviceReceived,
)
from chocolate_smart_home.schemas import DeviceReceived


def test_device_manager_create(empty_test_db):
    device_data = OnOffDeviceReceived(
        on=True,
        device=DeviceReceived(
            mqtt_id=123,
            device_type_name="on_off",
            remote_name="On Off Device - 1",
        ),
    )
    on_off_device = OnOffDeviceManager().create_device(device_data)
    assert on_off_device.id == 1
    assert on_off_device.on is True
    assert on_off_device.device.remote_name == "On Off Device - 1"
    assert on_off_device.device.mqtt_id == 123
    assert on_off_device.device.device_type.name == "on_off"


def test_device_manager_update(populated_test_db):
    device_data = OnOffDeviceReceived(
        on=True,
        device=DeviceReceived(
            mqtt_id=123,
            device_type_name="on_off",
            remote_name="On Off Device - 1",
        ),
    )
    on_off_device = OnOffDeviceManager().update_device(device_data)

    assert on_off_device.id == 1
    assert on_off_device.on is True
    assert on_off_device.device.remote_name == "On Off Device - 1"
    assert on_off_device.device.mqtt_id == 123
    assert on_off_device.device.device_type.name == "on_off"


def test_device_manager_update_fails_device_does_not_exist(empty_test_db):
    device_data = OnOffDeviceReceived(
        on=True,
        device=DeviceReceived(
            mqtt_id=123,
            device_type_name="on_off",
            remote_name="On Off Device - 1",
        ),
    )
    with pytest.raises(NoResultFound):
        OnOffDeviceManager().update_device(device_data)
