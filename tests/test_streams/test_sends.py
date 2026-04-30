from unittest.mock import Mock, patch

import pytest

from src import schemas, streams


@pytest.mark.asyncio
async def test_streams_sends_send_to_ws_service(mock_redis_session):
    await streams.send.send_to_ws_service(
        schemas.DeviceFrontend(
            device_type_name="example_device_type_name",
            last_seen=None,
            last_update_sent=None,
            mqtt_id=1,
            name="example_name",
            reboots=7,
            remote_name="example_remote_name",
            tags=None,
            plugin=None,
        )
    )
    mock_redis_session.xadd.assert_called_once_with(
        streams.stream_names.WEBSOCKETS_STREAM_NAME,
        {
            "message": (
                "{"
                '"remote_name": "example_remote_name", '
                '"name": "example_name", '
                '"reboots": 7, '
                '"mqtt_id": 1, '
                '"device_type_name": "example_device_type_name", '
                '"tags": null, '
                '"last_seen": null, '
                '"last_update_sent": null, '
                '"plugin": null'
                "}"
            )
        },
    )


@pytest.mark.asyncio
async def test_streams_sends_broadcast_db_state_to_client_calls_send_to_ws_service_with_device_frontend_schema(
    mock_redis_session, populated_test_db
):
    plugin_schema = None
    with (
        patch("src.streams.send.send_to_ws_service") as send_to_ws_service,
        patch("src.streams.send.schemas.DeviceFrontend") as DeviceFrontend,
    ):
        DeviceFrontend.return_value = "expected_return_value"
        await streams.send.broadcast_db_state_to_client(plugin_schema, 123)
        send_to_ws_service.assert_called_once_with("expected_return_value")


@pytest.mark.asyncio
async def test_streams_sends_broadcast_db_state_to_client_calls_device_frontend_schema_with_expected_parameters(
    mock_redis_session, populated_test_db
):
    plugin_schema = None
    with (
        patch("src.streams.send.send_to_ws_service"),
        patch("src.streams.send.schemas") as schemas,
    ):
        schemas.DeviceFrontend = Mock()
        await streams.send.broadcast_db_state_to_client(plugin_schema, 123)
        schemas.DeviceFrontend.assert_called_once_with(
            mqtt_id=123,
            remote_name="Remote Name 1 - 1",
            name="Test Device Name 1",
            device_type_name="TEST_DEVICE_TYPE_NAME_1",
            tags=[1, 2],
            reboots=0,
            last_seen="2025-01-02 00:00:00",
            last_update_sent="2025-01-01 00:00:00",
            plugin=None,
        )


@pytest.mark.asyncio
async def test_streams_sends_broadcast_db_state_to_client_raises_ValueError_when_given_invalid_mqtt_id(
    mock_redis_session, empty_test_db
):
    with pytest.raises(ValueError):
        await streams.send.broadcast_db_state_to_client(None, 123)
