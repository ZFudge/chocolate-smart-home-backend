from unittest.mock import patch

from src.plugins.BaseDeviceManager import BaseDeviceManager
from src.schemas.device import DeviceReceived


def test_BaseDeviceManager_create_device_calls_crud(empty_test_db):
    with patch("src.plugins.BaseDeviceManager.create_device") as create_device:
        BaseDeviceManager().create_device(1)
        create_device.assert_called_once_with(1)


def test_BaseDeviceManager_update_device_calls_crud(populated_test_db):
    with patch("src.plugins.BaseDeviceManager.update_device") as update_device:
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
        "src.plugins.BaseDeviceManager.get_device_by_id"
    ) as mock_get_device_by_id:
        BaseDeviceManager().get_device_by_id(123)
        mock_get_device_by_id.assert_called_once_with(123)
