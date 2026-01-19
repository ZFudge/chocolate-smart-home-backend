import logging
import os
import socket
import time
from typing import Callable, List

from paho.mqtt import MQTTException, client as mqtt

import src.mqtt.topics as topics
from src.mqtt.handler import mqtt_message_handler
from src.SingletonMeta import SingletonMeta


logger = logging.getLogger("mqtt")

DEFAULT_MQTT_HOST = "mqtt"
DEFAULT_MQTT_PORT = 1883


class MQTTClient(metaclass=SingletonMeta):
    def __init__(
        self,
        *,
        client_id_prefix: str = "",
        host: str = DEFAULT_MQTT_HOST,
        port: int = DEFAULT_MQTT_PORT,
        subscription_topics: List[str] = (topics.RECEIVE_DEVICE_DATA,),
        message_handler: Callable | None = None,
    ):
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
        self.subscribe_client_id()

    def subscribe_client_id(self):
        """
        Subscribing to this client's own client id, as a topic, allows for
        other clients, such as the virtual clients server, to validate that
        this client is connected to the mqtt broker, assuming that:
        1. the incoming message payload is the other client's client id, so
           that an appropriate response can be sent back to the other client
        2. the other client is subscribed to its own client id as a topic, so
           that it may receive the response.
        All of this is handled in MQTTClient.handle_client_id_message.
        """
        logger.info(f"Subscribing to client id: {self._client._client_id.decode()}")
        self.subscribe(
            topic=self._client._client_id.decode(),
            handler=self.handle_client_id_message,
        )

    def handle_client_id_message(self, _client, _userdata, message):
        logger.info("Received message: %s" % message.payload.decode())
        other_client_client_id = message.payload.decode()
        self.publish(topic=other_client_client_id, message=self._client._client_id.decode())

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
