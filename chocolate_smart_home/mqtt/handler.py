import asyncio
import logging
from typing import Callable, Dict

from paho.mqtt.client import Client, MQTTMessage
from sqlalchemy.exc import NoResultFound

from chocolate_smart_home.crud import get_device_by_mqtt_client_id
from chocolate_smart_home.models import Device
from chocolate_smart_home.plugins.discovered_plugins import (
    get_plugin_by_device_type,
)
from chocolate_smart_home.websocket.connection_manager import manager

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
        logger.info('Message received: "%s"' % payload)

        mqtt_id, device_type_name = payload.split(",")[:2]

        plugin: Dict = get_plugin_by_device_type(device_type_name)

        DuplexMessenger: Callable = plugin["DuplexMessenger"]
        DeviceManager: Callable = plugin["DeviceManager"]

        # Parse message data
        try:
            msg_data: Dict = DuplexMessenger().parse_msg(payload)
            logger.debug("msg_data %s" % msg_data)
        except StopIteration:
            raise

        # Broadcast message data through websocket, to all connected clients
        async def broadcast_to_fe_clients():
            fe_data = DuplexMessenger().serialize(msg_data)
            logger.info("Sending FE data %s" % fe_data)
            await manager.broadcast(fe_data)

        asyncio.run(broadcast_to_fe_clients())

        # Store client data in DB
        try:
            _: Device = get_device_by_mqtt_client_id(mqtt_id)
            logger.debug("found existing device %s" % _)
        except NoResultFound:
            return DeviceManager().create_device(msg_data)

        return DeviceManager().update_device(msg_data)
