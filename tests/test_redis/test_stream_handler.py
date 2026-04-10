import pytest

import src.schemas as schemas
from src.streams import send_to_ws_service, stream_names


@pytest.mark.asyncio
async def test_send_to_ws_service(redis_client):
    await send_to_ws_service(
        schemas.DeviceFrontend(
            device_type_name="example_device_type_name",
            last_seen=None,
            last_update_sent=None,
            mqtt_id=1,
            name="example_name",
            reboots=7,
            remote_name="example_remote_name",
            tags=None,
        )
    )
    redis_client.xadd.assert_called_once_with(
        stream_names.WS_STREAM_NAME,
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
                '"last_update_sent": null'
                "}"
            )
        },
    )
