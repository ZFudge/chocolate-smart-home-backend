import json
import logging
from typing import Iterable

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from chocolate_smart_home.mqtt import get_mqtt_client
from chocolate_smart_home.plugins.discovered_plugins import get_plugin_by_device_type
from chocolate_smart_home.schemas.websocket_msg import WebsocketMessage
from chocolate_smart_home.websocket.connection_manager import manager


mqtt_client = get_mqtt_client()

logger = logging.getLogger()

ws_router = APIRouter()


def handle_incoming_websocket_message(incoming_ws_data: dict):
    logger.info('Received incoming msg from websocket: "%s"' % (incoming_ws_data,))
    # Validate that the incoming websocket message has the required fields for
    # publishing via mqtt.
    try:
        ws_msg = WebsocketMessage(**incoming_ws_data)
    except ValidationError as e:
        logger.error("Invalid websocket message: %s" % e)
        return

    plugin = get_plugin_by_device_type(ws_msg.device_type_name)

    DuplexMessenger = plugin["DuplexMessenger"]
    try:
        complete_topics: Iterable[str] = DuplexMessenger().get_topics(ws_msg)
    except ValueError as e:
        logger.error("Error getting topics: %s" % e)
        return

    if "DuplexMessenger" not in plugin:
        logger.error("Plugin %s does not have a DuplexMessenger" % plugin)
        return
    DuplexMessenger = plugin["DuplexMessenger"]

    msg_data = {
        ws_msg.name: ws_msg.value,
    }
    outgoing_data = DuplexMessenger().compose_msg(msg_data)

    mqtt_client.publish_all(topics=complete_topics, message=outgoing_data)


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

        handle_incoming_websocket_message(incoming_ws_data)
