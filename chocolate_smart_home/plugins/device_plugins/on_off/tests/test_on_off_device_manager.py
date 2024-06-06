import pytest
from sqlalchemy.exc import NoResultFound

from chocolate_smart_home.plugins.device_plugins.on_off.device_manager import (
    OnOffDeviceManager,
)


def test_device_manager_create(empty_test_db):
    device_data = {
        "on": True,
        "mqtt_id": 123,
        "device_type_name": "on_off",
        "remote_name": "On Off Device - 1",
    }
    on_off_device = OnOffDeviceManager().create_device(device_data)

    assert on_off_device.id == 1
    assert on_off_device.on is True
    assert on_off_device.device.remote_name == "On Off Device - 1"
    assert on_off_device.device.client.mqtt_id == 123
    assert on_off_device.device.device_type.name == "on_off"


def test_device_manager_create_fails_missing_keys(empty_test_db):
    with pytest.raises(KeyError, match="on"):
        OnOffDeviceManager().create_device(
            {
                "mqtt_id": 123,
                "device_type_name": "on_off",
                "remote_name": "On Off Device - 1",
            }
        )


def test_device_manager_update(populated_test_db):
    device_data = {
        "on": True,
        "mqtt_id": 123,
        "device_type_name": "on_off",
        "remote_name": "On Off Device - 1",
    }
    on_off_device = OnOffDeviceManager().update_device(device_data)

    assert on_off_device.id == 1
    assert on_off_device.on is True
    assert on_off_device.device.remote_name == "On Off Device - 1"
    assert on_off_device.device.client.mqtt_id == 123
    assert on_off_device.device.device_type.name == "on_off"


def test_device_manager_update_fails_device_does_not_exist(empty_test_db):
    device_data = {
        "on": True,
        "mqtt_id": 123,
        "device_type_name": "on_off",
        "remote_name": "On Off Device - 1",
    }
    with pytest.raises(NoResultFound):
        OnOffDeviceManager().update_device(device_data)


def test_device_manager_update_fails_missing_keys(populated_test_db):
    with pytest.raises(KeyError, match="on"):
        OnOffDeviceManager().update_device(
            {
                "mqtt_id": 123,
                "device_type_name": "on_off",
                "remote_name": "On Off Device - 1",
            }
        )
    with pytest.raises(KeyError, match="mqtt_id"):
        OnOffDeviceManager().update_device(
            {
                "on": True,
                "device_type_name": "on_off",
                "remote_name": "On Off Device - 1",
            }
        )
    with pytest.raises(KeyError, match="device_type_name"):
        OnOffDeviceManager().update_device(
            {
                "on": True,
                "mqtt_id": 123,
                "remote_name": "On Off Device - 1",
            }
        )
    with pytest.raises(KeyError, match="remote_name"):
        OnOffDeviceManager().update_device(
            {
                "mqtt_id": 123,
                "on": True,
                "device_type_name": "on_off",
            }
        )
