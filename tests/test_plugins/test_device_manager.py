from unittest.mock import patch

from src.plugins.base_device_manager import BaseDeviceManager
from src.schemas.device import DeviceReceived


def test_base_device_manager_create_device_calls_crud(empty_test_db):
    with patch("src.plugins.base_device_manager.create_device") as create_device:
        BaseDeviceManager().create_device(1)
        create_device.assert_called_once_with(1)


def test_base_device_manager_update_device_calls_crud(populated_test_db):
    with patch("src.plugins.base_device_manager.update_device") as update_device:
        device = DeviceReceived(
            mqtt_id=123,
            device_type_name="test_device_type_name",
            remote_name="test_remote_name",
            name="test_remote_name",
        )
        BaseDeviceManager().update_device(device)
        update_device.assert_called_once_with(device)


def test_base_device_manager_get_device_by_id_calls_crud(populated_test_db):
    with patch(
        "src.plugins.base_device_manager.get_device_by_id"
    ) as mock_get_device_by_id:
        BaseDeviceManager().get_device_by_id(123)
        mock_get_device_by_id.assert_called_once_with(123)
