import json
import logging

from pydantic import ValidationError

from src import crud, schemas, streams
from src.plugins import PluginsManager
from src.pubsub.comm_funcs import publish, request_all_devices_data
from src.pubsub.topics import get_format_topic_by_mqtt_id_using_device_type_name

logger = logging.getLogger(__name__)


async def device_update_handler(message_data: dict):
    """Handle a device update message from Redis Streams.

    If the field is server-managed, update it and broadcast DB state to websocket clients.
    Otherwise, compose a controller message and publish it to the device over MQTT.
    """
    logger.info(f"Handling message: {message_data}")
    if message_data.get("action") == "request_all_devices_data":
        request_all_devices_data()
        return
    if isinstance(message_data.get("mqtt_id"), str):
        message_data["mqtt_id"] = json.loads(message_data["mqtt_id"])
    if isinstance(message_data.get("value"), str):
        try:
            message_data["value"] = eval(message_data["value"])
        except SyntaxError:
            pass
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
        if isinstance(incoming_ws_msg.mqtt_id, list):
            mqtt_ids = incoming_ws_msg.mqtt_id
        else:
            mqtt_ids = [incoming_ws_msg.mqtt_id]
        for mqtt_id in mqtt_ids:
            plugin_schema = DeviceManager().update_server_side_value(
                incoming_ws_msg.model_dump(), mqtt_id
            )
            await streams.send.broadcast_db_state_to_ws_client(plugin_schema, mqtt_id)
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
