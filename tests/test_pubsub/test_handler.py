from unittest.mock import MagicMock, Mock, patch

import pytest

from src.plugins.manager.classes import DEFAULT_PLUGIN
from src.pubsub.handler import mqtt_message_handler
from src import schemas


def test_pubsub_handler_returns_early_when_passed_none_payload(mqtt_message):
    mqtt_message.payload = None
    with (
        patch(
            "src.pubsub.handler.PluginsManager.get_plugin_by_device_type_name"
        ) as get_plugin_by_device_type_name,
        patch(
            "src.pubsub.handler.crud.set_last_seen_to_current_time"
        ) as set_last_seen_to_current_time,
    ):
        assert mqtt_message_handler(None, None, mqtt_message) is None
        get_plugin_by_device_type_name.assert_not_called()
        set_last_seen_to_current_time.assert_not_called()


def test_pubsub_handler_returns_expected_schema_when_passed_payload_of_only_mqtt_id(
    mqtt_message, empty_test_db
):
    mqtt_message.payload = b"777"
    device_frontend_schema = mqtt_message_handler(None, None, mqtt_message)
    assert device_frontend_schema.mqtt_id == 777
    assert device_frontend_schema.device_type_name == ""
    assert device_frontend_schema.remote_name == ""
    assert device_frontend_schema.name == ""
    assert device_frontend_schema.plugin is None
    assert device_frontend_schema.tags == []
    assert device_frontend_schema.reboots == 0
    assert device_frontend_schema.last_seen is None
    assert device_frontend_schema.last_update_sent is None


def test_pubsub_handler_calls_get_plugin_by_device_type_name(
    mqtt_message, empty_test_db
):
    with patch(
        "src.pubsub.handler.PluginsManager.get_plugin_by_device_type_name"
    ) as get_plugin_by_device_type_name:
        mqtt_message_handler(None, None, mqtt_message)
        get_plugin_by_device_type_name.assert_called_once_with("test_device_type_name")


def test_pubsub_handler_calls_ControllerToServerMessenger(mqtt_message, empty_test_db):
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


def test_pubsub_handler_returns_early_when_parse_controller_msg_raises_Exception(
    mqtt_message, empty_test_db
):
    controller_to_server_messenger = MagicMock()
    ControllerToServerMessenger = Mock(return_value=controller_to_server_messenger)
    with (
        patch.dict(
            DEFAULT_PLUGIN,
            {
                "ControllerToServerMessenger": ControllerToServerMessenger,
                "DeviceManager": MagicMock(),
            },
        ),
        patch("src.pubsub.handler.logger.error") as mock_logger,
    ):
        error = Exception("whoops")
        controller_to_server_messenger.parse_controller_msg = Mock(side_effect=error)

        assert mqtt_message_handler(None, None, mqtt_message) is None
        mock_logger.assert_called_once_with(error)


def test_pubsub_handler_DeviceManager_calls_create_device(mqtt_message, empty_test_db):
    device_manager = MagicMock()
    DeviceManager = Mock(return_value=device_manager)
    with patch.dict(DEFAULT_PLUGIN, {"DeviceManager": DeviceManager}):
        mqtt_message_handler(None, None, mqtt_message)
        DeviceManager.assert_called_once()
        device_manager.create_device.assert_called_once_with(
            schemas.DeviceReceived(
                device_type_name="test_device_type_name",
                remote_name="test_remote_name",
                name="test_remote_name",
                mqtt_id=123,
            ),
        )


def test_pubsub_handler_DeviceManager_calls_update_device(
    mqtt_message, populated_test_db
):
    device_manager = MagicMock()
    DeviceManager = Mock(return_value=device_manager)
    with patch.dict(DEFAULT_PLUGIN, {"DeviceManager": DeviceManager}):
        mqtt_message_handler(None, None, mqtt_message)
        DeviceManager.assert_called_once()
        device_manager.update_device.assert_called_once_with(
            schemas.DeviceReceived(
                device_type_name="test_device_type_name",
                remote_name="test_remote_name",
                name="test_remote_name",
                mqtt_id=123,
            ),
        )


def test_pubsub_handler_calls_set_last_seen_to_current_time(
    mqtt_message, empty_test_db
):
    with patch(
        "src.pubsub.handler.crud.set_last_seen_to_current_time", return_value=None
    ) as set_last_seen_to_current_time:
        mqtt_message_handler(None, None, mqtt_message)
        set_last_seen_to_current_time.assert_called_once_with(123)


def test_pubsub_handler_returns_early_when_passed_invalid_payload(mqtt_message):
    mqtt_message.payload = b"invalid"
    with (
        patch(
            "src.pubsub.handler.PluginsManager.get_plugin_by_device_type_name"
        ) as get_plugin_by_device_type_name,
        patch("src.pubsub.handler.logger.error") as mock_logger,
        patch(
            "src.pubsub.handler.crud.set_last_seen_to_current_time"
        ) as set_last_seen_to_current_time,
    ):
        assert mqtt_message_handler(None, None, mqtt_message) is None
        set_last_seen_to_current_time.assert_not_called()
        get_plugin_by_device_type_name.assert_not_called()
        mock_logger.assert_called_once_with('Received invalid payload: "invalid"')


@pytest.mark.asyncio
async def test_pubsub_handler_calls_send_to_ws_service(
    mqtt_message, mock_asyncio_event_loop, empty_test_db
):
    with (
        patch(
            "src.pubsub.handler.asyncio.run_coroutine_threadsafe",
        ) as run_coroutine_threadsafe,
        patch("src.pubsub.handler.schemas.DeviceFrontend") as DeviceFrontend,
        patch(
            "src.pubsub.handler.send_to_ws_service",
            # this avoids RuntimeWarning regarding coroutine not being awaited
            new_callable=lambda: Mock(),
        ) as send_to_ws_service,
    ):
        DeviceFrontend.return_value = Mock()
        assert (
            mqtt_message_handler(None, None, mqtt_message)
            is DeviceFrontend.return_value
        )
        run_coroutine_threadsafe.assert_called_once()
        send_to_ws_service.assert_called_once()


@pytest.mark.asyncio
async def test_pubsub_handler_handles_exception_on_coroutine(
    mqtt_message, mock_asyncio_event_loop, empty_test_db
):
    with (
        patch(
            "src.pubsub.handler.asyncio.run_coroutine_threadsafe",
            side_effect=Exception("oops"),
        ),
        patch("src.pubsub.handler.schemas.DeviceFrontend") as DeviceFrontend,
        patch(
            "src.pubsub.handler.send_to_ws_service",
            # this avoids RuntimeWarning regarding coroutine not being awaited
            new_callable=lambda: Mock(),
        ),
        patch("src.pubsub.handler.logger.error") as mock_logger,
    ):
        DeviceFrontend.return_value = Mock()
        mqtt_message_handler(None, None, mqtt_message)
        mock_logger.assert_called_once_with(
            "Error scheduling coroutine on redis streams event loop: oops"
        )


@pytest.mark.asyncio
async def test_pubsub_handler_loop_not_set(
    mqtt_message, empty_test_db, none_asyncio_event_loop
):
    with patch("src.pubsub.handler.logger.warning") as mock_logger:
        mqtt_message_handler(None, None, mqtt_message)
        mock_logger.assert_called_once_with(
            "Redis streams event loop not set. Cannot send message."
        )
