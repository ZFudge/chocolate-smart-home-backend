import json
import logging
from typing import Iterable

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from src.mqtt import get_mqtt_client
from src.plugins.discovered_plugins import get_plugin_by_device_type
from src.schemas.websocket_msg import WebsocketMessage
from src.websocket.connection_manager import manager


mqtt_client = get_mqtt_client()

logger = logging.getLogger()

ws_router = APIRouter()


async def handle_incoming_websocket_message(incoming_ws_data: dict):
    logger.info('Received incoming msg from FE websocket: "%s"' % (incoming_ws_data,))
    # Validate that the incoming websocket message has the required fields for
    # publishing via mqtt.
    try:
        ws_msg = WebsocketMessage(**incoming_ws_data)
    except ValidationError as e:
        logger.error("Invalid websocket message: %s" % e)
        return

    device_plugin = get_plugin_by_device_type(ws_msg.device_type_name)

    if "DeviceManager" not in device_plugin:
        logger.error("Plugin %s does not have a DeviceManager" % device_plugin)
        return
    DeviceManager = device_plugin["DeviceManager"]

    if "DuplexMessenger" not in device_plugin:
        logger.error("Plugin %s does not have a DuplexMessenger" % device_plugin)
        return
    DuplexMessenger = device_plugin["DuplexMessenger"]

    # Some values are only used server side, so we need to update the server side values
    if (
        hasattr(DeviceManager, "SERVER_SIDE_VALUES")
        and ws_msg.name in DeviceManager.SERVER_SIDE_VALUES
    ):
        # update device objects in the db with server side values
        logger.info("Updating server side values for Neo Pixel device %s" % ws_msg)
        DeviceManager().update_server_side_values(ws_msg)
        np_db_objects = DeviceManager().get_devices_by_mqtt_id(ws_msg.get_mqtt_ids())
        fe_data = DuplexMessenger().serialize_db_objects(np_db_objects)
        await manager.broadcast(fe_data)
        return

    try:
        complete_topics: Iterable[str] = DuplexMessenger().get_topics(ws_msg)
    except ValueError as e:
        logger.error("Error getting topics: %s" % e)
        return

    msg_data = {
        ws_msg.name: ws_msg.value,
    }
    outgoing_msg = DuplexMessenger().compose_msg(msg_data)

    if outgoing_msg:
        logger.info(
            "Publishing outgoing data to MQTT: %s, %s"
            % (complete_topics, outgoing_msg)
        )
        mqtt_client.publish_all(topics=complete_topics, message=outgoing_msg)


@ws_router.websocket_route("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket, mqtt_client)

    while True:
        try:
            incoming_data_str = await websocket.receive_text()
            incoming_ws_data = json.loads(incoming_data_str)
            logger.info("incoming_ws_data %s" % incoming_ws_data)
        except WebSocketDisconnect:
            logger.info("websocket disconnected")
            manager.disconnect(websocket)
            break

        await handle_incoming_websocket_message(incoming_ws_data)
