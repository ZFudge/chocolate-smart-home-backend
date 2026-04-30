import json
import logging

from pydantic import ValidationError

from src import crud, schemas, streams
from src.plugins import PluginsManager
from src.pubsub.comm_funcs import publish, request_all_devices_data
from src.pubsub.topics import get_format_topic_by_mqtt_id_using_device_type_name

logger = logging.getLogger(__name__)


async def handle_device_update(message_data: dict):
    logger.info(f"Handling message: {message_data}")
    if message_data.get("action") == "request_all_devices_data":
        request_all_devices_data()
        return
    if isinstance(message_data.get("mqtt_id"), str):
        message_data["mqtt_id"] = json.loads(message_data["mqtt_id"])
    try:
        incoming_ws_msg = schemas.WebsocketMessage(**message_data)
    except ValidationError:
        return
    # convert boolean strings back to boolean type
    if message_data["value"] in ("True", "False"):
        message_data["value"] = message_data["value"] == "True"
    elif isinstance(message_data["value"], str):
        try:
            message_data["value"] = json.loads(message_data["value"])
        except json.decoder.JSONDecodeError:
            pass

    plugin_mapping = PluginsManager.PLUGINS[incoming_ws_msg.device_type_name]
    DeviceManager = plugin_mapping["DeviceManager"]
    if DeviceManager.is_server_side_value(incoming_ws_msg.name):
        logger.info(
            f'Updating server side value: "{incoming_ws_msg.name}" to {incoming_ws_msg.value}'
        )
        logger.info(
            f'Updating server side value: "{incoming_ws_msg.name}" to {incoming_ws_msg.value}'
        )
        if isinstance(incoming_ws_msg.mqtt_id, list):
            for mqtt_id in incoming_ws_msg.mqtt_id:
                plugin_schema = DeviceManager().update_server_side_value(
                    incoming_ws_msg.model_dump(), mqtt_id
                )
                await streams.send.broadcast_db_state_to_client(plugin_schema, mqtt_id)
        else:
            plugin_schema = DeviceManager().update_server_side_value(
                incoming_ws_msg.model_dump(), incoming_ws_msg.mqtt_id
            )
            await streams.send.broadcast_db_state_to_client(
                plugin_schema, incoming_ws_msg.mqtt_id
            )
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
                try:
                    crud.set_last_update_sent_to_current_time(mqtt_id)
                except ValueError as e:
                    logger.warning("Could not set last_update_sent - %s" % e)
        else:
            topic = format_topic_by_mqtt_id(incoming_ws_msg.mqtt_id)
            publish(topic=topic, message=outgoing_controller_msg)
            try:
                crud.set_last_update_sent_to_current_time(incoming_ws_msg.mqtt_id)
            except ValueError as e:
                logger.warning("Could not set last_update_sent - %s" % e)
