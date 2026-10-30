from unittest.mock import patch

import pytest

from src import streams


@pytest.mark.asyncio
async def test_streams_reads__get_handle_reads_calls_xread(
    mocked_redis_session, populated_test_db
):
    message_data = {
        "mqtt_id": 123,
        "device_type_name": "device_type",
        "name": "count",
        "value": 5,
    }
    message_list = [
        (
            "message_id",
            message_data,
        ),
    ]
    messages = [("stream_name", message_list)]
    mocked_redis_session.xread.return_value = messages
    handle_reads = streams.reads._get_handle_reads()
    await handle_reads()
    mocked_redis_session.xread.assert_awaited_once_with(
        {"BACKEND_STREAM_NAME": "$"},
        count=1,
        block=1000,
    )


@pytest.mark.asyncio
async def test_streams_reads__get_handle_reads_calls_handle_input_message(
    mocked_redis_session,
):
    message_data = {
        "mqtt_id": 123,
        "device_type_name": "device_type",
        "name": "count",
        "value": 5,
    }
    message_list = [
        (
            "message_id",
            message_data,
        ),
    ]
    messages = [("stream_name", message_list)]
    mocked_redis_session.xread.return_value = messages
    with patch("src.streams.reads.device_update_handler") as device_update_handler:
        handle_reads = streams.reads._get_handle_reads()
        await handle_reads()
        device_update_handler.assert_called_once_with(message_data)


@pytest.mark.asyncio
async def test_read_server_side_value_triggers_broadcast(
    mocked_redis_session,
):
    message_data = {
        "mqtt_id": 123,
        "device_type_name": "device_type",
        "name": "server_side",
        "value": 5,
    }
    message_list = [
        (
            "message_id",
            message_data,
        ),
    ]
    messages = [("stream_name", message_list)]
    mocked_redis_session.xread.return_value = messages

    with (
        patch(
            "src.plugins.manager.PluginsManager.BaseDeviceManager.is_server_side_value",
            return_value=True,
        ),
        patch(
            "src.plugins.manager.PluginsManager.BaseDeviceManager.update_server_side_value",
            return_value="update_server_side_value__return_value",
        ),
        patch(
            "src.streams.device_update_handler.streams.send.broadcast_db_state_to_ws_client"
        ) as broadcast_db_state_to_ws_client,
    ):
        handle_reads = streams.reads._get_handle_reads()
        await handle_reads()
        broadcast_db_state_to_ws_client.assert_called_once_with(
            "update_server_side_value__return_value", 123
        )
