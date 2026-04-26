import logging
import os
from typing import Callable, Tuple

from paho.mqtt import MQTTException
from paho.mqtt.client import MQTTErrorCode

from .topics import REQUEST_DEVICE_DATA_ALL
from .validate_client_connection import validate_client_connection

logger = logging.getLogger(os.environ.get("LOGGER", "mqtt"))


@validate_client_connection
def publish(*, topic: str, message: str = "0", **kwargs) -> None:
    logger.info('Publishing message: "%s" through topic: %s...' % (message, topic))
    mqtt_client = kwargs.get("mqtt_client")

    (rc_update, message_id_update) = mqtt_client.publish(topic, message)
    if rc_update != MQTTErrorCode.MQTT_ERR_SUCCESS:
        err = "Failed! : %s rc_update: %s message_id_update: %s" % (
            message,
            rc_update,
            message_id_update,
        )
        logger.error(err)
        raise MQTTException(err)
    logger.info("Success")


def publish_all(*, topics: Tuple[str, ...], message: str = "", **kwargs) -> None:
    for topic in topics:
        publish(topic=topic, message=message, **kwargs)


@validate_client_connection
def subscribe(*, topic: str, handler: Callable, **kwargs) -> None:
    mqtt_client = kwargs.get("mqtt_client")
    logger.info("Subscribing to topic: %s" % topic)
    mqtt_client.subscribe(topic=topic)
    mqtt_client.message_callback_add(sub=topic, callback=handler)


def subscribe_all(*, topics: Tuple[str, ...], handler: Callable, **kwargs) -> None:
    for topic_for_sub in topics:
        subscribe(topic=topic_for_sub, handler=handler, **kwargs)


def request_all_devices_data() -> None:
    """Publishes an empty message to topic "/broadcast_request_devices_state/".
    All controllers are subscribed to this topic and will respond by publishing
    both their device-level configuration, and any relevant state values, back to
    the application, using topic "/receive_device_state/"."""
    logger.info('Publishing to topic: "%s"...' % REQUEST_DEVICE_DATA_ALL)
    publish(topic=REQUEST_DEVICE_DATA_ALL, message="")
