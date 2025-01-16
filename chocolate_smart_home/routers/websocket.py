import json
import logging
from typing import Iterable, List, TypedDict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from chocolate_smart_home.mqtt import mqtt_client_ctx
from chocolate_smart_home.plugins.discovered_plugins import get_plugin_by_device_type
from chocolate_smart_home.websocket.connection_manager import manager

logger = logging.getLogger()

ws_router = APIRouter()


class WebSocketMessage(TypedDict):
    device_type_name: str
    ids: List[int]
    name: str
    value: float | int | bool | List[str]


def handle_incoming_websocket_message(incoming_ws_data: WebSocketMessage):
    logger.info('received data from websocket: "%s"' % (incoming_ws_data,))

    # device type name is required to access plugin
    device_type_name = incoming_ws_data["device_type_name"]
    plugin = get_plugin_by_device_type(device_type_name)

    DuplexMessenger = plugin["DuplexMessenger"]
    complete_topics: Iterable[str] = DuplexMessenger().get_topics(
        device_type_name=device_type_name,
        data=incoming_ws_data
    )

    DuplexMessenger = plugin["DuplexMessenger"]

    msg_data = {
        incoming_ws_data["name"]: incoming_ws_data["value"],
    }
    outgoing_data = DuplexMessenger().compose_msg(msg_data)

    for topic in complete_topics:
        mqtt_client_ctx.get().publish(topic=topic, message=outgoing_data)


@ws_router.websocket_route("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    while True:
        try:
            incoming_data_str = await websocket.receive_text()
            incoming_ws_data = json.loads(incoming_data_str)
        except WebSocketDisconnect:
            logger.info("websocket disconnected")
            manager.disconnect(websocket)
            break

        handle_incoming_websocket_message(incoming_ws_data)
