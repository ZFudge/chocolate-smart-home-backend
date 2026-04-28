from unittest.mock import Mock

from ..Schema import NeoPixel


def test_neo_pixel_DeviceManager_create_device(
    DeviceManagerWithSuper_and_mocked_PluginModel,
):
    DeviceManagerWithSuper, PluginModel = DeviceManagerWithSuper_and_mocked_PluginModel
    mock_device_schema = Mock()
    mock_device_schema.mqtt_id = 1
    neo_pixel_schema = NeoPixel(
        on=True,
        twinkle=True,
        all_twinkle_colors_are_current=True,
        scheduled_palette_rotation=True,
        transform=True,
        ms=3,
        brightness=255,
        palette=(
            "#000",
            "#111",
            "#222",
            "#333",
            "#444",
            "#555",
            "#666",
            "#777",
            "#888",
        ),
        pir_enabled=True,
        pir_armed=True,
        pir_timeout=120,
    )
    mock_device_schema.plugin = neo_pixel_schema

    DeviceManagerWithSuper().create_device(mock_device_schema)
    BaseDeviceManager = DeviceManagerWithSuper.mro()[2]

    PluginModel.assert_called_once_with(
        mqtt_id=1,
        on=True,
        twinkle=True,
        all_twinkle_colors_are_current=True,
        scheduled_palette_rotation=True,
        transform=True,
        ms=3,
        brightness=255,
        palette=(
            "#000",
            "#111",
            "#222",
            "#333",
            "#444",
            "#555",
            "#666",
            "#777",
            "#888",
        ),
        pir_enabled=True,
        pir_armed=True,
        pir_timeout=120,
    )
    BaseDeviceManager.create_device.assert_called_once_with(mock_device_schema)
    BaseDeviceManager.update_device.assert_not_called()
    BaseDeviceManager.commit_db_object.assert_called_once_with(PluginModel.return_value)


def test_neo_pixel_DeviceManager_update_device(
    DeviceManagerWithSuper_and_mocked_PluginModel,
):
    DeviceManagerWithSuper, _ = DeviceManagerWithSuper_and_mocked_PluginModel
    mock_device_schema = Mock()
    mock_device_schema.mqtt_id = 1
    neo_pixel_schema = NeoPixel(
        on=True,
        twinkle=True,
        all_twinkle_colors_are_current=True,
        scheduled_palette_rotation=True,
        transform=True,
        ms=3,
        brightness=255,
        palette=(
            "#000",
            "#111",
            "#222",
            "#333",
            "#444",
            "#555",
            "#666",
            "#777",
            "#888",
        ),
        pir_enabled=True,
        pir_armed=True,
        pir_timeout=120,
    )
    mock_device_schema.plugin = neo_pixel_schema

    DeviceManagerWithSuper().update_device(mock_device_schema)
    BaseDeviceManager = DeviceManagerWithSuper.mro()[2]

    BaseDeviceManager.update_device.assert_called_once_with(mock_device_schema)
    BaseDeviceManager.create_device.assert_not_called()


def test_neo_pixel_DeviceManager_update_server_side_value(
    DeviceManagerWithSuper_and_mocked_PluginModel,
):
    DeviceManagerWithSuper, _ = DeviceManagerWithSuper_and_mocked_PluginModel
    data = {
        "device_type_name": "neo_pixel",
        "mqtt_id": 123,
        "name": "scheduled_palette_rotation",
        "value": True,
    }
    DeviceManagerWithSuper().update_server_side_value(data)
    BaseDeviceManager = DeviceManagerWithSuper.mro()[2]
    BaseDeviceManager.update_server_side_value.assert_called_once_with(data)
    BaseDeviceManager.create_device.assert_not_called()
    BaseDeviceManager.update_device.assert_not_called()
