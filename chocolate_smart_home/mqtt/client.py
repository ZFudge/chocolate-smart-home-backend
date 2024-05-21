import logging
from typing import Callable

import paho.mqtt.client as mqtt

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

    def __init__(self, *, host: str = DEFAULT_MQTT_HOST,
                          port: int = DEFAULT_MQTT_PORT):
        self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self._host = host
        self._port = port

    def connect(self):
        self._client.connect(
            self._host,
            self._port,
            60
        )
        self._client.loop_start()
        self._client.message_callback_add(
            topics.RECEIVE_DEVICE_DATA,
            MQTTMessageHandler().device_data_received
        )
        self._client.subscribe(topics.RECEIVE_DEVICE_DATA)

    def disconnect(self):
        self._client.disconnect()

    def publish(self, *, topic: str, message: str="0", callback: Callable = lambda x: None) -> bool:
        logger.info('Publishing message: "%s" through topic: "%s"...' % (message, topic))

        (rc_update, message_id_update) = self._client.publish(
            topic,
            message
        )
        if rc_update != mqtt.MQTT_ERR_SUCCESS:
            err = "Failed! : %s rc_update: %s message_id_update: %s" % (
                message,
                rc_update,
                message_id_update,
            )
            logger.error(err)
            callback(err)
            return False
        logger.info("Success")
        return True
