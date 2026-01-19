import json
import logging
import os
import time
from typing import Iterable

import websockets
from fastapi import WebSocket
from pydantic import ValidationError

from src.SingletonMeta import SingletonMeta
from src.crud import devices as devices_crud
from src.plugins.discovered_plugins import get_plugin_by_device_type
from src.schemas.websocket_msg import WebsocketMessage

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


SECRET = os.getenv("WEBSOCKET_SECRET", "")
WS_SERVICE_URL = f"ws://csm-ws-service:8050/ws/{SECRET}"


class WebsocketServiceConnector(metaclass=SingletonMeta):
    MAX_CONNECTION_ATTEMPTS: int = 10
    CONNECTION_ATTEMPT_DELAY: int = 7
    _mqtt_client = None
    _event_loop = None

    def __init__(self, mqtt_client=None):
        self.ws_service_connection: WebSocket | None = None
        self.connection_attempts = 0
        if mqtt_client is not None and WebsocketServiceConnector._mqtt_client is None:
            WebsocketServiceConnector._mqtt_client = mqtt_client
    
    @classmethod
    def set_event_loop(cls, loop):
        """Set the main event loop reference for thread-safe coroutine execution."""
        cls._event_loop = loop
    
    @classmethod
    def get_event_loop(cls):
        """Get the main event loop reference."""
        return cls._event_loop

    async def connect_to_websocket_service(self):
        """
        Connects to the external websocket service and relays messages back to the local server.
        """
        logger.info("Connecting to websocket service: %s" % WS_SERVICE_URL)
        if self.connection_attempts >= WebsocketServiceConnector.MAX_CONNECTION_ATTEMPTS:
            logger.error("Max connection attempts reached. Exiting.")
            return
        self.connection_attempts += 1
        try:
            async with websockets.connect(WS_SERVICE_URL) as websocket_service:
                logger.info("Successfully connected to websocket service")
                self.ws_service_connection = websocket_service
                self.connection_attempts = 0
                # Loop to receive messages from the websocket service
                while True:
                    websocket_service_data_str = await self.ws_service_connection.recv()
                    logger.info("Received data from websocket service: %s" % websocket_service_data_str)
                    websocket_service_data = json.loads(websocket_service_data_str)
                    if websocket_service_data.get("action") == "request_all_devices_data":
                        WebsocketServiceConnector._mqtt_client.request_all_devices_data()
                    else:
                        await self.handle_incoming_websocket_message(websocket_service_data)
        except ConnectionRefusedError:
            logger.error("Websocket service connection refused. "
                         "Check URL or server status. %s" % WS_SERVICE_URL)
            await self.reattempt_connection()
        except Exception as e:
            logger.error(f"Websocket service connection error: {e}")
            await self.reattempt_connection()

    async def reattempt_connection(self):
        """
        Attempts to connect to the websocket service after a connection error or closed connection.
        """
        self.connection_attempts += 1
        if self.connection_attempts_exceeded():
            logger.error("Max connection attempts reached. Exiting.")
            return
        logger.info("Waiting %s seconds to retry connection..." % WebsocketServiceConnector.CONNECTION_ATTEMPT_DELAY)
        time.sleep(WebsocketServiceConnector.CONNECTION_ATTEMPT_DELAY)
        logger.info("Trying again to connect to websocket service...")
        await self.connect_to_websocket_service()

    async def send_message_to_websocket_service(self, message: str | dict):
        logger.info(f"Sending message to websocket service: {message}")
        if isinstance(message, (dict, list)):
            message = json.dumps(message)
        if self.ws_service_connection:
            try:
                await self.ws_service_connection.send(message)
            except Exception as e:
                logger.error(f"Error sending message to websocket service: {e}")
                await self.reattempt_connection()
        else:
            logger.error("No connection established to websocket service")

    async def handle_incoming_websocket_message(self, incoming_ws_data: dict):
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

        mqtt_ids = ws_msg.get_mqtt_ids()
        # Some values are only used server side, so we need to update the server side values
        if (
            hasattr(DeviceManager, "SERVER_SIDE_VALUES")
            and ws_msg.name in DeviceManager.SERVER_SIDE_VALUES
        ):
            # update device objects in the db with server side values
            logger.info("Updating server side values for Neo Pixel device %s" % ws_msg)
            DeviceManager().update_server_side_values(ws_msg)
            np_db_objects = DeviceManager().get_devices_by_mqtt_id(mqtt_ids)
            fe_data = DuplexMessenger().serialize_db_objects(np_db_objects)
            await self.send_message_to_websocket_service(fe_data)
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
                "Publishing outgoing data to MQTT: %s, %s" % (complete_topics, outgoing_msg)
            )
            mqtt_client = WebsocketServiceConnector._mqtt_client
            if mqtt_client is not None:
                mqtt_client.publish_all(topics=complete_topics, message=outgoing_msg)
            for mqtt_id in mqtt_ids:
                devices_crud.update_last_update_sent_if_exists(mqtt_id)

    def connection_attempts_exceeded(self):
        return self.connection_attempts >= WebsocketServiceConnector.MAX_CONNECTION_ATTEMPTS

    async def disconnect(self):
        if self.ws_service_connection:
            logger.info("Closing websocket service connection...")
            await self.ws_service_connection.close()
            logger.info("Websocket service connection closed")
        self.ws_service_connection = None
