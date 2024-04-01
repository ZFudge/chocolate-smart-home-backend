from sqlalchemy.orm import Session
import paho.mqtt.client as mqtt

from chocolate_smart_home import schemas
from chocolate_smart_home.mqtt import handlers, topics

DEFAULT_MQTT_PORT = 1883

class MQTTClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, *, host: str, port: int = DEFAULT_MQTT_PORT):
        self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self._host = host
        self._port = port

    def connect(self):
        self._client.connect(self._host, self._port, 60)
        self._client.loop_start()

        self._client.message_callback_add(topics.RECEIVE_DEVICE_DATA,
                                          handlers.device_data_received)
        self._client.subscribe(topics.RECEIVE_DEVICE_DATA)

    def disconnect(self):
        self._client.disconnect()

    def publish(self, topic, message="0", callback=lambda x: None):
        print(
            'Publishing message: "%s" through topic: "%s"...' % (message, topic)
        )
        (rc_update, message_id_update) = self._client.publish(topic, message)
        if rc_update != mqtt.MQTT_ERR_SUCCESS:
            err = "Failed! : %s rc_update: %s message_id_update: %s" % (
                message,
                rc_update,
                message_id_update,
            )
            print(err)
            callback(err)
        else:
            print("Success")