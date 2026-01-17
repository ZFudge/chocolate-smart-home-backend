import logging
import os
import socket
import time
from typing import Callable, List

from paho.mqtt import MQTTException, client as mqtt

import src.mqtt.topics as topics
from src.mqtt.handler import mqtt_message_handler


logger = logging.getLogger("mqtt")

DEFAULT_MQTT_HOST = "127.0.0.1"
DEFAULT_MQTT_PORT = 1883


class MQTTClient:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        *,
        host: str = DEFAULT_MQTT_HOST,
        port: int = DEFAULT_MQTT_PORT,
        client_id_prefix: str = "",
        subscription_topics: List[str] = (topics.RECEIVE_DEVICE_DATA,),
        message_handler: Callable | None = None,
    ):
        if self._initialized:
            return

        client_id = client_id_prefix + os.environ.get(
            "MQTT_CLIENT_ID", "CSM-FASTAPI-SERVER"
        )
        logger.info(
            "Initializing MQTT client with client_id %s, host %s, and port %s"
            % (client_id, host, port)
        )
        self.subscription_topics = subscription_topics
        self.message_handler = message_handler if message_handler is not None else mqtt_message_handler
        self._client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, client_id=client_id
        )
        self._host = host
        self._port = port
        self._initialized = True

    def subscribe_all(self) -> None:
        for topic_for_sub in self.subscription_topics:
            self._client.subscribe(topic_for_sub)
            self._client.message_callback_add(topic_for_sub, self.message_handler)

    def connect(self):
        logger.info("Connecting MQTT client to %s:%s" % (self._host, self._port))
        if self._client.is_connected():
            logger.info("MQTT client is already connected")
            return

        try:
            self._client.connect(self._host, self._port, 60)
        except socket.gaierror as e:
            logger.error("Failed to connect to the MQTT broker: %s" % e)
            # Wait 15 seconds before retrying connection to the mqtt broker
            time.sleep(15)
            return

        self._client.loop_start()
        self.subscribe_all()

    def is_connected(self):
        return self._client.is_connected()

    def disconnect(self):
        logger.info("Disconnecting MQTT client from %s:%s" % (self._host, self._port))
        self._client.disconnect()

    def publish(
        self,
        *,
        topic: str,
        message: str = "0",
        callback: Callable = lambda x: None,
        **kwargs,
    ) -> None:
        logger.info('Publishing message: "%s" through topic: %s...' % (message, topic))
        if not self._client.is_connected():
            logger.error("MQTT client is not connected to the MQTT broker")
            return

        (rc_update, message_id_update) = self._client.publish(topic, message)
        if rc_update != mqtt.MQTT_ERR_SUCCESS:
            err = "Failed! : %s rc_update: %s message_id_update: %s" % (
                message,
                rc_update,
                message_id_update,
            )
            logger.error(err)
            callback(err)
            raise MQTTException(err)
        logger.info("Success")

    def publish_all(self, *, topics: List[str], **kwargs) -> None:
        for topic in topics:
            self.publish(topic=topic, **kwargs)

    def subscribe(self, *, topic: str, handler: Callable) -> None:
        logger.info("Subscribing to topic: %s" % topic)
        self._client.subscribe(topic)
        self._client.message_callback_add(topic, handler)

    def request_all_devices_data(self) -> None:
        """Publishes an empty message to topic "/broadcast_request_devices_state/".
        All controllers are subscribed to this topic and will respond by publishing
        both their device-level configuration, and any relevant state values, back to
        the application, using topic "/receive_device_state/"."""
        logger.info('Publishing to topic: "%s"...' % topics.REQUEST_DEVICE_DATA_ALL)

        self.publish(topic=topics.REQUEST_DEVICE_DATA_ALL, message="")
