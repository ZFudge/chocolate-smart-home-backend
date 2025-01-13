import logging
import os
from typing import Callable

from paho.mqtt import MQTTException, client as mqtt

import chocolate_smart_home.mqtt.topics as topics
from chocolate_smart_home.mqtt.handler import MQTTMessageHandler


logger = logging.getLogger("mqtt")

DEFAULT_MQTT_HOST = "127.0.0.1"
DEFAULT_MQTT_PORT = 1883


class MQTTClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        *,
        host: str = DEFAULT_MQTT_HOST,
        port: int = DEFAULT_MQTT_PORT,
        client_id_prefix: str = ""
    ):
        client_id = client_id_prefix + os.environ.get(
            "MQTT_CLIENT_ID", "CSM-FASTAPI-SERVER"
        )
        logger.info(
            "Initializing MQTT client with client_id %s, host %s, and port %s"
            % (client_id, host, port)
        )
        self._client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, client_id=client_id
        )
        self._host = host
        self._port = port

    def connect(self):
        logger.info("Connecting MQTT client to %s:%s" % (self._host, self._port))
        self._client.connect(self._host, self._port, 60)
        self._client.loop_start()
        self._client.subscribe(topics.RECEIVE_DEVICE_DATA)
        self._client.message_callback_add(
            topics.RECEIVE_DEVICE_DATA, MQTTMessageHandler().device_data_received
        )

    def disconnect(self):
        logger.info("Disconnecting MQTT client from %s:%s" % (self._host, self._port))
        self._client.disconnect()

    def publish(
        self, *, topic: str, message: str = "0", callback: Callable = lambda x: None
    ) -> None:
        logger.info('Publishing message: "%s" through topic: %s...' % (message, topic))

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

    def request_all_devices_data(self) -> None:
        """Publishes an empty message to topic "/broadcast_request_devices_state/".
        All controllers are subscribed to this topic and will respond by publishing
        both their device-level configuration, and any relevant state values, back to
        the application, using topic "/receive_device_state/"."""
        logger.info('Publishing to topic: "%s"...' % topics.REQUEST_DEVICE_DATA_ALL)

        self.publish(topic=topics.REQUEST_DEVICE_DATA_ALL, message="")
