from fastapi import WebSocket, WebSocketDisconnect
import logging

logger = logging.getLogger()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, data_message: dict):
        logger.info(
            "Broadcasting message to all connected clients %s %s"
            % (self.active_connections, data_message)
        )
        for connection in self.active_connections:
            try:
                await connection.send_json(data=data_message)
            except WebSocketDisconnect:
                self.disconnect(connection)


manager = ConnectionManager()
