import asyncio
import logging
from typing import Callable, Dict, List

from paho.mqtt.client import Client, MQTTMessage
from pydantic import ValidationError
from sqlalchemy.exc import NoResultFound

from src.crud import get_devices_by_mqtt_id
from src.models import Device
from src.plugins.discovered_plugins import (
    get_plugin_by_device_type,
)
from src.websocket.WebsocketServiceConnector import WebsocketServiceConnector as WSC

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

    # Store client data in DB
    db_plugin_device: Device | None = None
    try:
        _: Device | List[Device] = get_devices_by_mqtt_id(mqtt_id)
        logger.debug("found existing device %s" % _)
        if isinstance(_, list):
            raise NotImplementedError(
                "Multiple devices with the same mqtt_id are not supported"
            )
    except NoResultFound:
        db_plugin_device = DeviceManager().create_device(msg_data)
    else:
        db_plugin_device = DeviceManager().update_device(msg_data)

    # Broadcast message data through websocket, to all connected clients
    async def broadcast_through_websocket_service(pd: Device | None):
        if pd is None:
            return
        if hasattr(DuplexMessenger, "serialize_db_objects"):
            fe_data = DuplexMessenger().serialize_db_objects(pd)
        elif hasattr(DuplexMessenger, "serialize_db_obj"):
            fe_data = DuplexMessenger().serialize_db_obj(pd)
        else:
            fe_data = DuplexMessenger().serialize(msg_data)
        logger.info("Sending FE data %s" % fe_data)
        try:
            await WSC().send_message_to_websocket_service(fe_data)
        except Exception as e:
            logger.error(f"Error sending message to websocket service: {e}")
            return

    # Schedule the coroutine on the main event loop from the MQTT thread
    event_loop = WSC.get_event_loop()
    if event_loop is not None:
        try:
            asyncio.run_coroutine_threadsafe(
                broadcast_through_websocket_service(db_plugin_device),
                event_loop
            )
        except Exception as e:
            logger.error(f"Error scheduling coroutine on event loop: {e}")
    else:
        logger.warning("Event loop not set in WebsocketServiceConnector. Cannot send message to websocket service.")

    return db_plugin_device
