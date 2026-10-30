from unittest.mock import MagicMock, call, patch

import pytest

from src.schemas import WebsocketMessage
from src.streams.device_update_handler import device_update_handler


@pytest.mark.asyncio
async def test_device_update_handler_calls_request_all_devices_data(
    mocked_redis_session,
    none_asyncio_event_loop,
):
    message_data = {"action": "request_all_devices_data"}
    with patch(
        "src.streams.device_update_handler.request_all_devices_data"
    ) as request_all_devices_data:
        await device_update_handler(message_data)
        request_all_devices_data.assert_called_once()


@pytest.mark.asyncio
async def test_device_update_handler_casts_boolean_strs(populated_test_db):
    message_data = {
        "mqtt_id": 123,
        "device_type_name": "device_type",
        "name": "something",
        "value": "True",
    }
    await device_update_handler(message_data)
    assert message_data["value"] is True
    message_data = {
        "mqtt_id": 123,
        "device_type_name": "device_type",
        "name": "something",
        "value": "False",
    }
    await device_update_handler(message_data)
    assert message_data["value"] is False


@pytest.mark.asyncio
async def test_device_update_handler_loads_json_str(populated_test_db):
    message_data = {
        "mqtt_id": 123,
        "device_type_name": "device_type",
        "name": "something",
        "value": "[1,2]",
    }
    await device_update_handler(message_data)
    assert message_data["value"] == [1, 2]


@pytest.mark.asyncio
async def test_device_update_handler_loads_mqtt_list_str(populated_test_db):
    message_data = {
        "mqtt_id": "[123,234]",
        "device_type_name": "device_type",
        "name": "something",
        "value": "",
    }
    await device_update_handler(message_data)
    assert message_data["mqtt_id"] == [123, 234]


@pytest.mark.asyncio
async def test_device_update_handler_returns_early_from_failed_validation(
    populated_test_db,
):
    await device_update_handler(
        {
            "mqtt_id": "[123,234]",
            "device_type_name": "device_type",
            "name": "something",
        }
    )


@pytest.mark.asyncio
async def test_device_update_handler_logs_failure_to_set_last_update_sent(
    mqtt_client,
    empty_test_db,
):
    with patch("src.streams.device_update_handler.logger.warning") as mock_logger:
        await device_update_handler(
            {
                "mqtt_id": 123,
                "device_type_name": "device_type",
                "name": "something",
                "value": "",
            }
        )
        mock_logger.assert_called_once_with(
            "Could not set last_update_sent - Device with mqtt_id 123 not found"
        )
    with patch("src.streams.device_update_handler.logger.warning") as mock_logger:
        await device_update_handler(
            {
                "mqtt_id": "[123,234]",
                "device_type_name": "device_type",
                "name": "something",
                "value": "",
            }
        )
        mock_logger.assert_has_calls(
            [
                call(
                    "Could not set last_update_sent - Device with mqtt_id 123 not found"
                ),
                call(
                    "Could not set last_update_sent - Device with mqtt_id 234 not found"
                ),
            ]
        )


@pytest.mark.asyncio
async def test_device_update_handler_is_server_side_value_single(
    mqtt_client,
    empty_test_db,
):
    with (
        patch(
            "src.plugins.bases.BaseDeviceManager.BaseDeviceManager.is_server_side_value",
            return_value=True,
        ),
        patch(
            "src.streams.device_update_handler.streams.send.broadcast_db_state_to_ws_client"
        ) as broadcast_db_state_to_ws_client,
    ):
        await device_update_handler(
            {
                "mqtt_id": 123,
                "device_type_name": "device_type",
                "name": "something",
                "value": "",
            }
        )
        broadcast_db_state_to_ws_client.assert_awaited_once()


@pytest.mark.asyncio
async def test_device_update_handler_is_server_side_value_multiple(
    mqtt_client,
    empty_test_db,
):
    with (
        patch(
            "src.plugins.bases.BaseDeviceManager.BaseDeviceManager.is_server_side_value",
            return_value=True,
        ),
        patch(
            "src.streams.device_update_handler.streams.send.broadcast_db_state_to_ws_client"
        ) as broadcast_db_state_to_ws_client,
    ):
        await device_update_handler(
            {
                "mqtt_id": "[123,234]",
                "device_type_name": "device_type",
                "name": "something",
                "value": "",
            }
        )
        assert broadcast_db_state_to_ws_client.call_count == 2


@pytest.mark.asyncio
async def test_device_update_handler_casts_string_bool_to_bool_type(
    mqtt_client,
    populated_test_db,
):
    message_data = {
        "mqtt_id": "123",
        "device_type_name": "device_type",
        "name": "something",
        "value": "True",
    }
    expected_message_data_transform = message_data | {"mqtt_id": 123, "value": True}
    with patch("src.streams.device_update_handler.schemas") as mock_schemas:
        mock_schemas.WebsocketMessage = MagicMock(
            return_value=WebsocketMessage(**expected_message_data_transform)
        )
        await device_update_handler(message_data)
        mock_schemas.WebsocketMessage.assert_called_once_with(
            **expected_message_data_transform
        )
