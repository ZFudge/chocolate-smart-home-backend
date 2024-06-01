import logging
from typing import Callable, Dict

from paho.mqtt.client import Client, MQTTMessage
from sqlalchemy.exc import NoResultFound

from chocolate_smart_home.crud import get_device_by_mqtt_id
from chocolate_smart_home.models import Device
from chocolate_smart_home.plugins.discovered_plugins import (
    get_device_plugin_by_device_type,
)


logger = logging.getLogger("mqtt")


class MQTTMessageHandler:
    def device_data_received(
        self,
        _client: Client,
        _userdata: None,
        message: MQTTMessage,
    ) -> Device | None:
        payload: str = message.payload.decode()
        logger.info('Message received: "%s"' % payload)
        if payload is None:
            return

        mqtt_id, device_type_name = payload.split(",")[:2]

        plugin: Dict = get_device_plugin_by_device_type(device_type_name)

        MessageHandler: Callable = plugin["DuplexMessenger"]
        DeviceManager: Callable = plugin["DeviceManager"]

        try:
            msg_data: Dict = MessageHandler().parse_msg(payload)
        except StopIteration:
            raise StopIteration(
                f"Not enough comma-separated values in message.payload. {payload=}."
            ) from None

        try:
            _: Device = get_device_by_mqtt_id(mqtt_id)
        except NoResultFound:
            return DeviceManager().create_device(msg_data)

        return DeviceManager().update_device(msg_data)
