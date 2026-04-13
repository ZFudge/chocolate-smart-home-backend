from unittest.mock import MagicMock, Mock, patch

from src.pubsub.handler import mqtt_message_handler
from src.plugins.PluginsManager import DEFAULT_PLUGIN
from src.schemas.device import DeviceReceived


def test_get_plugin_by_device_type_name_called_mqtt_message_handler(
    mqtt_message, empty_test_db
):
    with patch(
        "src.pubsub.handler.PluginsManager.get_plugin_by_device_type_name"
    ) as get_plugin_by_device_type_name:
        mqtt_message_handler(None, None, mqtt_message)
        get_plugin_by_device_type_name.assert_called_once_with("test_device_type_name")


def test_ControllerToServerMessenger_called_mqtt_message_handler(
    mqtt_message, empty_test_db
):
    controller_to_server_messenger = MagicMock()
    ControllerToServerMessenger = Mock(return_value=controller_to_server_messenger)
    with patch.dict(
        DEFAULT_PLUGIN,
        {
            "ControllerToServerMessenger": ControllerToServerMessenger,
            "DeviceManager": MagicMock(),
        },
    ):
        mqtt_message_handler(None, None, mqtt_message)
        ControllerToServerMessenger.assert_called_once()
        controller_to_server_messenger.parse_controller_msg.assert_called_once_with(
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
        "src.pubsub.handler.get_device_by_id", return_value=None
    ) as get_device_by_id:
        mqtt_message_handler(None, None, mqtt_message)
        get_device_by_id.assert_called_once_with(123)


def test_none_payload_mqtt_message_handler(mqtt_message):
    mqtt_message.payload = None
    with (
        patch(
            "src.pubsub.handler.PluginsManager.get_plugin_by_device_type_name"
        ) as get_plugin_by_device_type_name,
        patch("src.pubsub.handler.get_device_by_id") as get_device_by_id,
    ):
        mqtt_message_handler(None, None, mqtt_message)
        get_plugin_by_device_type_name.assert_not_called()
        get_device_by_id.assert_not_called()


def test_invalid_payload_mqtt_message_handler(mqtt_message):
    mqtt_message.payload = b"invalid"
    with (
        patch(
            "src.pubsub.handler.PluginsManager.get_plugin_by_device_type_name"
        ) as get_plugin_by_device_type_name,
        patch("src.pubsub.handler.logger.error") as mock_logger,
        patch("src.pubsub.handler.get_device_by_id") as get_device_by_id,
    ):
        get_device_by_id.assert_not_called()
        mqtt_message_handler(None, None, mqtt_message)
        get_plugin_by_device_type_name.assert_not_called()
        mock_logger.assert_called_once_with('Received invalid payload: "invalid"')
