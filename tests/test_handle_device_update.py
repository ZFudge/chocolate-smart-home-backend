from unittest.mock import call, patch

import pytest

from src.handle_device_update import handle_device_update


@pytest.mark.asyncio
async def test_handle_device_update_calls_request_all_devices_data(mock_redis_session):
    message_data = {"action": "request_all_devices_data"}
    with patch(
        "src.handle_device_update.request_all_devices_data"
    ) as request_all_devices_data:
        await handle_device_update(message_data)
        request_all_devices_data.assert_called_once()


@pytest.mark.asyncio
async def test_handle_device_update_casts_boolean_strs(populated_test_db):
    message_data = {
        "mqtt_id": 123,
        "device_type_name": "device_type",
        "name": "something",
        "value": "True",
    }
    await handle_device_update(message_data)
    assert message_data["value"] is True
    message_data = {
        "mqtt_id": 123,
        "device_type_name": "device_type",
        "name": "something",
        "value": "False",
    }
    await handle_device_update(message_data)
    assert message_data["value"] is False


@pytest.mark.asyncio
async def test_handle_device_update_loads_json_str(populated_test_db):
    message_data = {
        "mqtt_id": 123,
        "device_type_name": "device_type",
        "name": "something",
        "value": "[1,2]",
    }
    await handle_device_update(message_data)
    assert message_data["value"] == [1, 2]


@pytest.mark.asyncio
async def test_handle_device_update_loads_mqtt_list_str(populated_test_db):
    message_data = {
        "mqtt_id": "[123,234]",
        "device_type_name": "device_type",
        "name": "something",
        "value": "",
    }
    await handle_device_update(message_data)
    assert message_data["mqtt_id"] == [123, 234]


@pytest.mark.asyncio
async def test_handle_device_update_returns_early_from_failed_validation(
    populated_test_db,
):
    await handle_device_update(
        {
            "mqtt_id": "[123,234]",
            "device_type_name": "device_type",
            "name": "something",
        }
    )


@pytest.mark.asyncio
async def test_handle_device_update_logs_failure_to_set_last_update_sent(
    mqtt_client,
    empty_test_db,
):
    with patch("src.handle_device_update.logger.warning") as mock_logger:
        await handle_device_update(
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
    with patch("src.handle_device_update.logger.warning") as mock_logger:
        await handle_device_update(
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
async def test_handle_device_update_is_server_side_value_single(
    mqtt_client,
    empty_test_db,
):
    with (
        patch(
            "src.plugins.BaseDeviceManager.BaseDeviceManager.is_server_side_value",
            return_value=True,
        ),
        patch(
            "src.handle_device_update.streams.send.broadcast_db_state_to_client"
        ) as broadcast_db_state_to_client,
    ):
        await handle_device_update(
            {
                "mqtt_id": 123,
                "device_type_name": "device_type",
                "name": "something",
                "value": "",
            }
        )
        broadcast_db_state_to_client.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_device_update_is_server_side_value_multiple(
    mqtt_client,
    empty_test_db,
):
    with (
        patch(
            "src.plugins.BaseDeviceManager.BaseDeviceManager.is_server_side_value",
            return_value=True,
        ),
        patch(
            "src.handle_device_update.streams.send.broadcast_db_state_to_client"
        ) as broadcast_db_state_to_client,
    ):
        await handle_device_update(
            {
                "mqtt_id": "[123,234]",
                "device_type_name": "device_type",
                "name": "something",
                "value": "",
            }
        )
        broadcast_db_state_to_client.call_count == 2
