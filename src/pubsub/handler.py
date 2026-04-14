import logging
from typing import Callable, Dict

from paho.mqtt.client import Client, MQTTMessage
from pydantic import ValidationError

from src.crud import get_device_by_id
from src.plugins import PluginsManager
from src.schemas.device import DeviceReceived as DeviceReceivedSchema


logger = logging.getLogger("mqtt")


def mqtt_message_handler(
    _client: Client,
    _userdata: None,
    message: MQTTMessage,
) -> DeviceReceivedSchema | None:
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

    device_plugin: Dict = PluginsManager.get_plugin_by_device_type_name(
        device_type_name
    )

    ControllerToServerMessenger: Callable = device_plugin["ControllerToServerMessenger"]
    DeviceManager: Callable = device_plugin["DeviceManager"]

    # Parse message data
    try:
        device_received_schema: DeviceReceivedSchema = (
            ControllerToServerMessenger().parse_controller_msg(payload)
        )
    except StopIteration as e:
        logger.error(e)
        return
    except ValidationError as e:
        logger.error(e)
        return

    # Store client data in DB
    existing_device = get_device_by_id(mqtt_id)
    if existing_device is None:
        DeviceManager().create_device(device_received_schema)
    else:
        DeviceManager().update_device(device_received_schema)

    # device_received_schema still contains most recent values
    # and should be broadcast to frontend

    return device_received_schema
