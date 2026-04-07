from unittest.mock import MagicMock, Mock, patch

import pytest
from paho.mqtt.client import MQTTMessage

from src.mqtt.handler import mqtt_message_handler
from src.plugins.discovered_plugins import DEFAULT_PLUGIN
from src.schemas.device import DeviceReceived


@pytest.fixture
def mqtt_message():
    message = MQTTMessage()
    message.payload = b"123,test_device_type_name,test_remote_name"
    yield message


def test_get_plugin_by_device_type_name_called_mqtt_message_handler(
    mqtt_message, empty_test_db
):
    with patch(
        "src.mqtt.handler.get_plugin_by_device_type_name"
    ) as get_plugin_by_device_type_name:
        mqtt_message_handler(None, None, mqtt_message)
        get_plugin_by_device_type_name.assert_called_once_with("test_device_type_name")


def test_DuplexMessenger_called_mqtt_message_handler(mqtt_message, empty_test_db):
    duplex_messenger = MagicMock()
    DuplexMessenger = Mock(return_value=duplex_messenger)
    with patch.dict(
        DEFAULT_PLUGIN,
        {"DuplexMessenger": DuplexMessenger, "DeviceManager": MagicMock()},
    ):
        mqtt_message_handler(None, None, mqtt_message)
        DuplexMessenger.assert_called_once()
        duplex_messenger.parse_msg.assert_called_once_with(
            "123,test_device_type_name,test_remote_name"
        )


def test_DeviceManager_create_device_called_mqtt_message_handler(
    mqtt_message, empty_test_db
):
    device_manager = MagicMock()
    DeviceManager = Mock(return_value=device_manager)
    with patch.dict(DEFAULT_PLUGIN, {"DeviceManager": DeviceManager}):
        mqtt_message_handler(None, None, mqtt_message)
        DeviceManager.assert_called_once()
        device_manager.create_device.assert_called_once_with(
            DeviceReceived(
                device_type_name="test_device_type_name",
                remote_name="test_remote_name",
                name="test_remote_name",
                mqtt_id=123,
            ),
        )


def test_DeviceManager_update_device_called_mqtt_message_handler(
    mqtt_message, populated_test_db
):
    device_manager = MagicMock()
    DeviceManager = Mock(return_value=device_manager)
    with patch.dict(DEFAULT_PLUGIN, {"DeviceManager": DeviceManager}):
        mqtt_message_handler(None, None, mqtt_message)
        DeviceManager.assert_called_once()
        device_manager.update_device.assert_called_once_with(
            DeviceReceived(
                device_type_name="test_device_type_name",
                remote_name="test_remote_name",
                name="test_remote_name",
                mqtt_id=123,
            ),
        )


def test_get_device_by_id_called_mqtt_message_handler(mqtt_message, empty_test_db):
    with patch(
        "src.mqtt.handler.get_device_by_id", return_value=None
    ) as get_device_by_id:
        mqtt_message_handler(None, None, mqtt_message)
        get_device_by_id.assert_called_once_with(123)


def test_none_payload_mqtt_message_handler(mqtt_message):
    mqtt_message.payload = None
    with (
        patch(
            "src.mqtt.handler.get_plugin_by_device_type_name"
        ) as get_plugin_by_device_type_name,
        patch("src.mqtt.handler.get_device_by_id") as get_device_by_id,
    ):
        mqtt_message_handler(None, None, mqtt_message)
        get_plugin_by_device_type_name.assert_not_called()
        get_device_by_id.assert_not_called()


def test_invalid_payload_mqtt_message_handler(mqtt_message):
    mqtt_message.payload = b"invalid"
    with (
        patch(
            "src.mqtt.handler.get_plugin_by_device_type_name"
        ) as get_plugin_by_device_type_name,
        patch("src.mqtt.handler.logger.error") as mock_logger,
        patch("src.mqtt.handler.get_device_by_id") as get_device_by_id,
    ):
        get_device_by_id.assert_not_called()
        mqtt_message_handler(None, None, mqtt_message)
        get_plugin_by_device_type_name.assert_not_called()
        mock_logger.assert_called_once_with('Received invalid payload: "invalid"')
