from unittest.mock import patch

import pytest

from src import streams


@pytest.mark.asyncio
async def test_streams_reads__get_handle_reads_calls_xread(
    mock_redis_session, populated_test_db
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
    mock_redis_session.xread.return_value = messages
    handle_reads = streams.reads._get_handle_reads()
    await handle_reads()
    mock_redis_session.xread.assert_called_once_with(
        {"BACKEND_STREAM_NAME": "$"},
        count=1,
        block=1000,
    )


@pytest.mark.asyncio
async def test_streams_reads__get_handle_reads_calls_handle_input_message(
    mock_redis_session,
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
    mock_redis_session.xread.return_value = messages
    with patch("src.streams.reads.handle_device_update") as handle_device_update:
        handle_reads = streams.reads._get_handle_reads()
        await handle_reads()
        handle_device_update.assert_called_once_with(message_data)
