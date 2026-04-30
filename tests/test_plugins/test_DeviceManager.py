from unittest.mock import patch

import pytest

from src.plugins.BaseDeviceManager import BaseDeviceManager
from src.schemas.device import DeviceReceived


def test_BaseDeviceManager_create_device_calls_crud(empty_test_db):
    with patch("src.plugins.BaseDeviceManager.crud.create_device") as create_device:
        BaseDeviceManager().create_device(1)
        create_device.assert_called_once_with(1)


def test_BaseDeviceManager_update_device_calls_crud(populated_test_db):
    with patch("src.plugins.BaseDeviceManager.crud.update_device") as update_device:
        device = DeviceReceived(
            mqtt_id=123,
            device_type_name="test_device_type_name",
            remote_name="test_remote_name",
            name="test_remote_name",
        )
        BaseDeviceManager().update_device(device)
        update_device.assert_called_once_with(device)


def test_BaseDeviceManager_get_device_by_id_calls_crud(populated_test_db):
    with patch(
        "src.plugins.BaseDeviceManager.crud.get_device_by_id"
    ) as mock_get_device_by_id:
        BaseDeviceManager().get_device_by_id(123)
        mock_get_device_by_id.assert_called_once_with(123)


def test_BaseDeviceManager_update_server_side_value_fails_if_not_server_side_value(
    empty_test_db,
):
    with pytest.raises(
        ValueError, match='"not_a_server_side_value" is not a server-side value'
    ):
        BaseDeviceManager().update_server_side_value(
            {
                "name": "not_a_server_side_value",
                "value": "test_value",
                "device_type_name": "test_device_type_name",
                "mqtt_id": 123,
            }
        )


def test_BaseDeviceManager_update_server_side_value_fails_validation(empty_test_db):
    with pytest.raises(ValueError):
        BaseDeviceManager().update_server_side_value({})
