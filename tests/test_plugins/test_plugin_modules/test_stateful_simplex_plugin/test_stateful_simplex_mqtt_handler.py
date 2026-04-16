from unittest.mock import MagicMock, Mock

from src.crud import get_device_by_id, get_plugin_db_obj_using_device_type_and_mqtt_id
from src.plugins import PluginsManager
from src.pubsub.handler import mqtt_message_handler
from src.schemas import DeviceFrontend as DeviceFrontendSchema
from tests.test_plugins.test_plugin_modules.test_stateful_simplex_plugin.stateful_simplex_plugin.Schema import (
    StatefulSimplexPluginSchema,
)


def test_stateful_simplex_handler_returns_device_received_schema(
    mqtt_message, stateful_simplex_plugin_path, empty_test_db
):
    PluginsManager.load_plugin_from_path(stateful_simplex_plugin_path)
    mqtt_message.payload = b"123,stateful_simplex_plugin,test_remote_name,7"
    device_schema = mqtt_message_handler(None, None, mqtt_message)
    assert isinstance(device_schema, DeviceFrontendSchema)
    assert (
        device_schema.model_dump()
        == DeviceFrontendSchema(
            mqtt_id=123,
            device_type_name="stateful_simplex_plugin",
            remote_name="test_remote_name",
            name="test_remote_name",
            tags=[],
            reboots=0,
            last_seen=None,
            last_update_sent=None,
            plugin=StatefulSimplexPluginSchema(sensor_reading=7),
        ).model_dump()
    )


def test_stateful_simplex_handler_creates_primary_device(
    mqtt_message, stateful_simplex_plugin_path, empty_test_db
):
    PluginsManager.load_plugin_from_path(stateful_simplex_plugin_path)
    mqtt_message.payload = b"123,stateful_simplex_plugin,test_remote_name,7"
    mqtt_message_handler(None, None, mqtt_message)
    device = get_device_by_id(123)
    assert device is not None
    assert device.mqtt_id == 123


def test_stateful_simplex_handler_creates_plugin_device(
    mqtt_message, stateful_simplex_plugin_path, empty_test_db
):
    PluginsManager.load_plugin_from_path(stateful_simplex_plugin_path)
    mqtt_message.payload = b"123,stateful_simplex_plugin,test_remote_name,7"
    mqtt_message_handler(None, None, mqtt_message)
    assert (
        get_plugin_db_obj_using_device_type_and_mqtt_id(
            "stateful_simplex_plugin", 123
        ).sensor_reading
        == 7
    )


def test_stateful_simplex_handler_updates_plugin_device(
    mqtt_message, stateful_simplex_plugin_path, empty_test_db
):
    PluginsManager.load_plugin_from_path(stateful_simplex_plugin_path)
    mqtt_message.payload = b"123,stateful_simplex_plugin,test_remote_name,13"
    mqtt_message_handler(None, None, mqtt_message)
    mqtt_message.payload = b"123,stateful_simplex_plugin,test_remote_name,28"
    mqtt_message_handler(None, None, mqtt_message)
    assert (
        get_plugin_db_obj_using_device_type_and_mqtt_id(
            "stateful_simplex_plugin", 123
        ).sensor_reading
        == 28
    )


def test_stateful_simplex_handler_calls_plugin_DeviceManager_create_device(
    mqtt_message, stateful_simplex_plugin_path, empty_test_db
):
    PluginsManager.load_plugin_from_path(stateful_simplex_plugin_path)

    device_manager = MagicMock()
    DeviceManager = Mock(return_value=device_manager)
    PluginsManager.PLUGINS["stateful_simplex_plugin"]["DeviceManager"] = DeviceManager

    mqtt_message.payload = b"123,stateful_simplex_plugin,test_remote_name,7"
    mqtt_message_handler(None, None, mqtt_message)

    DeviceManager.assert_called_once()
    device_manager.create_device.assert_called_once()
    device_manager.update_device.assert_not_called()


def test_stateful_simplex_handler_calls_plugin_DeviceManager_update_device(
    mqtt_message, stateful_simplex_plugin_path, empty_test_db
):
    PluginsManager.load_plugin_from_path(stateful_simplex_plugin_path)

    mqtt_message.payload = b"123,stateful_simplex_plugin,test_remote_name,7"
    mqtt_message_handler(None, None, mqtt_message)

    device_manager = MagicMock()
    DeviceManager = Mock(return_value=device_manager)
    PluginsManager.PLUGINS["stateful_simplex_plugin"]["DeviceManager"] = DeviceManager

    mqtt_message.payload = b"123,stateful_simplex_plugin,test_remote_name,99"
    mqtt_message_handler(None, None, mqtt_message)
    DeviceManager.assert_called_once()
    device_manager.create_device.assert_not_called()
    device_manager.update_device.assert_called_once()
