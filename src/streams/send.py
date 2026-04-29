import json
import logging

from src import crud, dependencies, schemas
from . import stream_names

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def send_to_ws_service(device_data: schemas.DeviceFrontend):
    data = device_data.model_dump()
    message_data = dict(message=json.dumps(data))
    await dependencies.redis_session.get().xadd(
        stream_names.WEBSOCKETS_STREAM_NAME, message_data
    )


async def broadcast_db_state_to_client(plugin_schema, mqtt_id):
    primary_device = crud.get_device_by_id(mqtt_id)
    frontend_schema = schemas.DeviceFrontend(
        mqtt_id=mqtt_id,
        remote_name=primary_device.remote_name,
        name=primary_device.name,
        device_type_name=primary_device.device_type.name,
        tags=[t.id for t in primary_device.tags],
        reboots=primary_device.reboots,
        last_seen=(str(primary_device.last_seen) if primary_device.last_seen else None),
        last_update_sent=(
            str(primary_device.last_update_sent)
            if primary_device.last_update_sent
            else None
        ),
        plugin=plugin_schema,
    )
    await send_to_ws_service(frontend_schema)
