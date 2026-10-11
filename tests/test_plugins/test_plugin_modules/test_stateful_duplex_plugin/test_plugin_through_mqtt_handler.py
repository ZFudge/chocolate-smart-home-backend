from unittest.mock import MagicMock, Mock

from src.crud import get_device_by_id, get_plugin_db_obj_using_device_type_and_mqtt_id
from src.plugins import PluginsManager
from src.pubsub.handler import mqtt_message_handler
from src.schemas import DeviceFrontend as DeviceFrontendSchema
from tests.test_plugins.test_plugin_modules.test_stateful_duplex_plugin.stateful_duplex_plugin.Schema import (
    StatefulDuplexPluginSchema,
)


def test_stateful_duplex_handler_returns_device_received_schema(
    mqtt_message, stateful_duplex_plugin_path, empty_test_db
):
    PluginsManager.load_plugin_from_path(stateful_duplex_plugin_path)
    mqtt_message.payload = b"123,stateful_duplex_plugin,test_remote_name,7"
    device_schema = mqtt_message_handler(None, None, mqtt_message)
    assert isinstance(device_schema, DeviceFrontendSchema)
    model_data = device_schema.model_dump()
    assert (
        model_data
        == DeviceFrontendSchema(
            mqtt_id=123,
            device_type_name="stateful_duplex_plugin",
            remote_name="test_remote_name",
            name="test_remote_name",
            tags=[],
            reboots=0,
            last_seen=model_data.get("last_seen"),
            last_update_sent=None,
            plugin=StatefulDuplexPluginSchema(count=7),
            online=True,
        ).model_dump()
    )


def test_stateful_duplex_handler_creates_primary_device(
    mqtt_message, stateful_duplex_plugin_path, empty_test_db
):
    PluginsManager.load_plugin_from_path(stateful_duplex_plugin_path)
    mqtt_message.payload = b"123,stateful_duplex_plugin,test_remote_name,7"
    mqtt_message_handler(None, None, mqtt_message)
    device = get_device_by_id(123)
    assert device is not None
    assert device.mqtt_id == 123


def test_stateful_duplex_handler_creates_plugin_device(
    mqtt_message, stateful_duplex_plugin_path, empty_test_db
):
    PluginsManager.load_plugin_from_path(stateful_duplex_plugin_path)
    mqtt_message.payload = b"123,stateful_duplex_plugin,test_remote_name,7"
    mqtt_message_handler(None, None, mqtt_message)
    assert (
        get_plugin_db_obj_using_device_type_and_mqtt_id(
            "stateful_duplex_plugin", 123
        ).count
        == 7
    )


def test_stateful_duplex_handler_updates_plugin_device(
    mqtt_message, stateful_duplex_plugin_path, empty_test_db
):
    PluginsManager.load_plugin_from_path(stateful_duplex_plugin_path)
    mqtt_message.payload = b"123,stateful_duplex_plugin,test_remote_name,13"
    mqtt_message_handler(None, None, mqtt_message)
    mqtt_message.payload = b"123,stateful_duplex_plugin,test_remote_name,28"
    mqtt_message_handler(None, None, mqtt_message)
    assert (
        get_plugin_db_obj_using_device_type_and_mqtt_id(
            "stateful_duplex_plugin", 123
        ).count
        == 28
    )


def test_stateful_duplex_handler_calls_plugin_DeviceManager_create_device(
    mqtt_message, stateful_duplex_plugin_path, empty_test_db
):
    PluginsManager.load_plugin_from_path(stateful_duplex_plugin_path)

    device_manager = MagicMock()
    DeviceManager = Mock(return_value=device_manager)
    PluginsManager.PLUGINS["stateful_duplex_plugin"]["DeviceManager"] = DeviceManager

    mqtt_message.payload = b"123,stateful_duplex_plugin,test_remote_name,7"
    mqtt_message_handler(None, None, mqtt_message)

    DeviceManager.assert_called_once()
    device_manager.create_device.assert_called_once()
    device_manager.update_device.assert_not_called()


def test_stateful_duplex_handler_calls_plugin_DeviceManager_update_device(
    mqtt_message, stateful_duplex_plugin_path, empty_test_db
):
    PluginsManager.load_plugin_from_path(stateful_duplex_plugin_path)

    mqtt_message.payload = b"123,stateful_duplex_plugin,test_remote_name,7"
    mqtt_message_handler(None, None, mqtt_message)

    device_manager = MagicMock()
    DeviceManager = Mock(return_value=device_manager)
    PluginsManager.PLUGINS["stateful_duplex_plugin"]["DeviceManager"] = DeviceManager

    mqtt_message.payload = b"123,stateful_duplex_plugin,test_remote_name,99"
    mqtt_message_handler(None, None, mqtt_message)
    DeviceManager.assert_called_once()
    device_manager.create_device.assert_not_called()
    device_manager.update_device.assert_called_once()
