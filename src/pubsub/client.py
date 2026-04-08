# import logging
# import os
# import socket
# import time
# from typing import Callable, Tuple

# from paho.mqtt import MQTTException, client as mqtt

# import src.mqtt.topics as topics
# from src.mqtt.handler import mqtt_message_handler
# from src.SingletonMeta import SingletonMeta


# logger = logging.getLogger("mqtt")

# DEFAULT_MQTT_HOST = os.environ.get("MQTT_HOST", "mqtt")
# DEFAULT_MQTT_PORT = int(os.environ.get("MQTT_PORT", 1883))
# CLIENT_SUFFIX = os.environ.get("MQTT_CLIENT_ID", "CSM-FASTAPI-SERVER")


# class MQTTClient(metaclass=SingletonMeta):
#     def __init__(
#         self,
#         *,
#         client_id_prefix: str = "",
#         host: str = DEFAULT_MQTT_HOST,
#         port: int = DEFAULT_MQTT_PORT,
#         subscription_topics: Tuple[str, ...] = (topics.RECEIVE_DEVICE_DATA,),
#         message_handler: Callable | None = None,
#     ):
#         client_id = "_".join([client_id_prefix, CLIENT_SUFFIX])
#         logger.info(
#             f"Initializing MQTT client with client_id {client_id}, host {host}, and port {port}"
#         )
#         self.subscription_topics = subscription_topics
#         self.message_handler = message_handler or mqtt_message_handler
#         self._client = mqtt.Client(
#             mqtt.CallbackAPIVersion.VERSION2, client_id=client_id
#         )
#         self._host = host
#         self._port = port

#     def connect(self):
#         logger.info("Connecting MQTT client to %s:%s" % (self._host, self._port))
#         if self._client.is_connected():
#             logger.info("MQTT client is already connected")
#             return

#         try:
#             self._client.connect(self._host, self._port, 60)
#         except socket.gaierror as e:
#             logger.error("Failed to connect to the MQTT broker: %s" % e)
#             # Wait 15 seconds before retrying connection to the mqtt broker
#             time.sleep(15)
#             return
#         except MQTTException as e:
#             logger.error("MQTT exception: %s" % e)
#             # Wait 15 seconds before retrying connection to the mqtt broker
#             time.sleep(15)
#             return
#         except Exception as e:
#             logger.error("Failed to connect to the MQTT broker: %s" % e)
#             # Wait 15 seconds before retrying connection to the mqtt broker
#             time.sleep(15)
#             return

#         logger.info("Starting MQTT client loop")
#         try:
#             self._client.loop_start()
#         except mqtt.MQTTErrorCode as e:
#             logger.error("Failed to start MQTT client loop: %s" % e)
#             # Wait 15 seconds before retrying connection to the mqtt broker
#             time.sleep(15)
#             return

#         self.subscribe_all()

#     def is_connected(self):
#         return self._client.is_connected()

#     def disconnect(self):
#         logger.info("Disconnecting MQTT client from %s:%s" % (self._host, self._port))
#         self._client.disconnect()

#     def publish_all(self, *, topics: Tuple[str, ...], **kwargs) -> None:
#         for topic in topics:
#             self.publish(topic=topic, **kwargs)

#     def publish(
#         self,
#         *,
#         topic: str,
#         message: str = "0",
#         **kwargs,
#     ) -> None:
#         logger.info('Publishing message: "%s" through topic: %s...' % (message, topic))
#         if not self._client.is_connected():
#             logger.error("MQTT client is not connected to the MQTT broker")
#             return

#         (rc_update, message_id_update) = self._client.publish(
#             topic=topic, message=message
#         )
#         if rc_update != mqtt.MQTT_ERR_SUCCESS:
#             err = "Failed! : %s rc_update: %s message_id_update: %s" % (
#                 message,
#                 rc_update,
#                 message_id_update,
#             )
#             logger.error(err)
#             raise MQTTException(err)
#         logger.info("Success")

#     def subscribe(self, *, topic: str, handler: Callable) -> None:
#         logger.info("Subscribing to topic: %s" % topic)
#         self._client.subscribe(topic=topic)
#         self._client.message_callback_add(sub=topic, callback=handler)

#     def subscribe_all(self) -> None:
#         for topic_for_sub in self.subscription_topics:
#             self._client.subscribe(topic=topic_for_sub)
#             self._client.message_callback_add(
#                 sub=topic_for_sub, callback=self.message_handler
#             )

#     def request_all_devices_data(self) -> None:
#         """Publishes an empty message to topic "/broadcast_request_devices_state/".
#         All controllers are subscribed to this topic and will respond by publishing
#         both their device-level configuration, and any relevant state values, back to
#         the application, using topic "/receive_device_state/"."""
#         logger.info('Publishing to topic: "%s"...' % topics.REQUEST_DEVICE_DATA_ALL)
#         self.publish(topic=topics.REQUEST_DEVICE_DATA_ALL, message="")
