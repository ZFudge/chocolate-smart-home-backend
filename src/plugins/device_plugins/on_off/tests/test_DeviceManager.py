from unittest.mock import Mock

from ..Schema import OnOff


def test_on_off_DeviceManager_create_device(
    DeviceManagerWithSuper_and_mocked_PluginModel,
):
    DeviceManagerWithSuper, PluginModel = DeviceManagerWithSuper_and_mocked_PluginModel
    mock_device_schema = Mock()
    mock_device_schema.mqtt_id = 1
    on_off_schema = OnOff(on=True)
    mock_device_schema.plugin = on_off_schema

    DeviceManagerWithSuper().create_device(mock_device_schema)
    BaseDeviceManager = DeviceManagerWithSuper.mro()[2]

    PluginModel.assert_called_once_with(
        mqtt_id=1,
        on=True,
    )
    BaseDeviceManager.create_device.assert_called_once_with(mock_device_schema)
    BaseDeviceManager.update_device.assert_not_called()
    BaseDeviceManager.commit_db_object.assert_called_once_with(PluginModel.return_value)


def test_on_off_DeviceManager_update_device(
    DeviceManagerWithSuper_and_mocked_PluginModel,
):
    DeviceManagerWithSuper, _ = DeviceManagerWithSuper_and_mocked_PluginModel
    mock_device_schema = Mock()
    mock_device_schema.mqtt_id = 1
    on_off_schema = OnOff(on=True)
    mock_device_schema.plugin = on_off_schema

    DeviceManagerWithSuper().update_device(mock_device_schema)
    BaseDeviceManager = DeviceManagerWithSuper.mro()[2]

    BaseDeviceManager.update_device.assert_called_once_with(mock_device_schema)
    BaseDeviceManager.create_device.assert_not_called()
