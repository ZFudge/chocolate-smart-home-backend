import asyncio
import logging
from typing import Callable, Dict

from paho.mqtt.client import Client, MQTTMessage
from pydantic import ValidationError
from sqlalchemy.exc import NoResultFound

from src.crud import get_device_by_mqtt_id
from src.models import Device
from src.plugins.discovered_plugins import (
    get_plugin_by_device_type,
)
from src.websocket.connection_manager import manager

logger = logging.getLogger("mqtt")


class MQTTMessageHandler:
    def device_data_received(
        self,
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

        device_plugin: Dict = get_plugin_by_device_type(device_type_name)

        DuplexMessenger: Callable = device_plugin["DuplexMessenger"]
        DeviceManager: Callable = device_plugin["DeviceManager"]

        # Parse message data
        try:
            msg_data: Dict = DuplexMessenger().parse_msg(payload)
            logger.info("msg_data %s" % msg_data)
        except StopIteration as e:
            logger.error(e)
            return
        except ValidationError as e:
            logger.error(e)
            return

        # Broadcast message data through websocket, to all connected clients
        async def broadcast_to_fe_clients():
            fe_data = DuplexMessenger().serialize(msg_data)
            logger.info("Sending FE data %s" % fe_data)
            await manager.broadcast(fe_data)

        asyncio.run(broadcast_to_fe_clients())

        # Store client data in DB
        try:
            _: Device = get_device_by_mqtt_id(mqtt_id)
            logger.debug("found existing device %s" % _)
        except NoResultFound:
            return DeviceManager().create_device(msg_data)

        return DeviceManager().update_device(msg_data)
