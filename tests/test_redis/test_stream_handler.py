import pytest

from src import schemas, streams


@pytest.mark.asyncio
async def test_send_to_ws_service(redis_client):
    await streams.send_to_ws_service(
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
    redis_client.xadd.assert_called_once_with(
        streams.stream_names.WS_STREAM_NAME,
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
