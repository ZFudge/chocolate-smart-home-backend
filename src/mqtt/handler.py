import logging

from paho.mqtt.client import Client, MQTTMessage

from src.crud import get_device_by_id
from src.models import Device


logger = logging.getLogger("mqtt")


def mqtt_message_handler(
    _client: Client,
    _userdata: None,
    message: MQTTMessage,
) -> Device | None:
    if message.payload is None:
        return

    payload: str = message.payload.decode()
    logger.info('Message received from "%s": "%s"' % (message.topic, payload))

    try:
        mqtt_id, device_type_name = payload.split(",")[:2]
    except ValueError:
        logger.error("Invalid payload: %s" % payload)
        return

    logger.info("MQTT ID: %s, Device Type Name: %s" % (mqtt_id, device_type_name))
    mqtt_id = int(mqtt_id)
    device = get_device_by_id(mqtt_id)
    logger.info("Device: %s" % device)

    return device
