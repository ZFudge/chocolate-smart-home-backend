import logging
from typing import Dict, Callable

from paho.mqtt.client import Client, MQTTMessage
from pydantic import ValidationError

from src.crud import get_device_by_id
from src.models import Device as Device_model
from src.plugins.discovered_plugins import get_plugin_by_device_type
from src.schemas.device import DeviceReceived as DeviceReceivedSchema


logger = logging.getLogger("mqtt")


def mqtt_message_handler(
    _client: Client,
    _userdata: None,
    message: MQTTMessage,
) -> Device_model | None:
    if message.payload is None:
        return

    payload: str = message.payload.decode()
    logger.info('Message received from "%s": "%s"' % (message.topic, payload))

    try:
        mqtt_id: int = int(payload.split(",")[0])
        device_type_name: str = payload.split(",")[1]
    except ValueError:
        logger.error('Received invalid payload: "%s"' % payload)
        return

    device_plugin: Dict = get_plugin_by_device_type(device_type_name)

    DuplexMessenger: Callable = device_plugin["DuplexMessenger"]
    DeviceManager: Callable = device_plugin["DeviceManager"]

    # Parse message data
    try:
        device_received: DeviceReceivedSchema = DuplexMessenger().parse_msg(payload)
    except StopIteration as e:
        logger.error(e)
        return
    except ValidationError as e:
        logger.error(e)
        return

    # Store client data in DB
    existing_device = get_device_by_id(mqtt_id)
    if existing_device is None:
        db_plugin_device = DeviceManager().create_device(device_received)
    else:
        db_plugin_device = DeviceManager().update_device(device_received)

    return db_plugin_device
