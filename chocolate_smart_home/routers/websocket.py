import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from chocolate_smart_home.websocket.connection_manager import manager

logger = logging.getLogger()

ws_router = APIRouter()


@ws_router.websocket_route("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    while True:
        try:
            incoming_data = await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            break
        counter = int(incoming_data) * 2 - 1
        logger.info("counter %s" % (counter,))
        await websocket.send_json(dict(counter=counter))
