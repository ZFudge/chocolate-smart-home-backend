from fastapi import WebSocket, WebSocketDisconnect
import logging

from src.mqtt.topics import REQUEST_DEVICE_DATA_ALL

logger = logging.getLogger()


class ConnectionManager:
    def __init__(self):
        logger.info("ConnectionManager initialized")
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket, client):
        await websocket.accept()
        self.active_connections.append(websocket)

        if not hasattr(client, "publish"):
            logger.error("MQTT client does not have a publish method")
            return
        try:
            # sync client and controller data
            client.publish(topic=REQUEST_DEVICE_DATA_ALL, message="0")
        except Exception as e:
            logger.error("Error publishing to MQTT client: %s" % e)

    def disconnect(self, websocket: WebSocket):
        logger.info("Client disconnected")
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        logger.info("Sending message to client")
        await websocket.send_text(message)

    async def broadcast(self, data_message: dict):
        logger.info(
            "Broadcasting message to all connected clients: %s, msg: %s"
            % (self.active_connections, data_message)
        )
        for connection in self.active_connections:
            try:
                if isinstance(data_message, list):
                    for item in data_message:
                        await connection.send_json(data=item)
                else:
                    await connection.send_json(data=data_message)
            except WebSocketDisconnect:
                self.disconnect(connection)
            except Exception as e:
                logger.error("Error sending message to client: %s" % e)


manager = ConnectionManager()
