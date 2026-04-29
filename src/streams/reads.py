import asyncio
import json
import logging

from pydantic import ValidationError

from src import crud, schemas
from src.dependencies import redis_session
from src.plugins import PluginsManager
from src.pubsub.comm_funcs import publish, request_all_devices_data
from src.pubsub.topics import get_format_topic_by_mqtt_id_using_device_type_name
from . import send, stream_names

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def handle_message(message_data: dict):
    logger.info(f"Handling message: {message_data}")
    if message_data.get("action") == "request_all_devices_data":
        request_all_devices_data()
        return
    # convert boolean strings back to boolean type
    if message_data["value"] in ("True", "False"):
        message_data["value"] = message_data["value"] == "True"
    elif isinstance(message_data["value"], str):
        try:
            message_data["value"] = json.loads(message_data["value"])
        except json.decoder.JSONDecodeError:
            pass
    if isinstance(message_data["mqtt_id"], str):
        message_data["mqtt_id"] = json.loads(message_data["mqtt_id"])
    try:
        incoming_ws_msg = schemas.WebsocketMessage(**message_data)
    except ValidationError:
        return

    plugin_mapping = PluginsManager.PLUGINS[incoming_ws_msg.device_type_name]
    DeviceManager = plugin_mapping["DeviceManager"]
    if DeviceManager.is_server_side_value(incoming_ws_msg.name):
        logger.info(
            f'Updating server side value: "{incoming_ws_msg.name}" to {incoming_ws_msg.value}'
        )
        # Plugin schema should exist because only plugins that implement their own model will have server side values
        plugin_schema = DeviceManager().update_server_side_value(
            incoming_ws_msg.model_dump()
        )
        primary_device = crud.get_device_by_id(incoming_ws_msg.mqtt_id)
        frontend_schema = schemas.DeviceFrontend(
            mqtt_id=incoming_ws_msg.mqtt_id,
            remote_name=primary_device.remote_name,
            name=primary_device.name,
            device_type_name=primary_device.device_type.name,
            tags=[t.id for t in primary_device.tags],
            reboots=primary_device.reboots,
            last_seen=(
                str(primary_device.last_seen) if primary_device.last_seen else None
            ),
            last_update_sent=(
                str(primary_device.last_update_sent)
                if primary_device.last_update_sent
                else None
            ),
            plugin=plugin_schema,
        )
        await send.send_to_ws_service(frontend_schema)
    else:
        logger.info(
            f'Composing controller message from data: "{incoming_ws_msg.model_dump()}'
        )
        format_topic_by_mqtt_id = get_format_topic_by_mqtt_id_using_device_type_name(
            incoming_ws_msg.device_type_name
        )
        ServerToControllerMessenger = plugin_mapping["ServerToControllerMessenger"]
        outgoing_controller_msg = ServerToControllerMessenger().compose_controller_msg(
            incoming_ws_msg.model_dump()
        )
        if isinstance(incoming_ws_msg.mqtt_id, list):
            for mqtt_id in incoming_ws_msg.mqtt_id:
                topic = format_topic_by_mqtt_id(mqtt_id)
                publish(topic=topic, message=outgoing_controller_msg)
        else:
            topic = format_topic_by_mqtt_id(incoming_ws_msg.mqtt_id)
            publish(topic=topic, message=outgoing_controller_msg)


async def handle_reads():
    last_id = "$"
    while True:
        try:
            messages = await redis_session.get().xread(
                {stream_names.BACKEND_STREAM_NAME: last_id},
                count=1,
                block=1000,
            )
            if messages:
                logger.info(f"Received messages: {messages}")
                for stream_name, message_list in messages:
                    logger.info(f"Stream name: {stream_name}")
                    for message_id, message_data in message_list:
                        logger.info(
                            f"Received message ID: {message_id}, Data: {message_data}"
                        )
                        last_id = message_id  # Update the last received ID
                        await handle_message(message_data)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error("Error handling messages: %s" % e)
            await asyncio.sleep(1)
