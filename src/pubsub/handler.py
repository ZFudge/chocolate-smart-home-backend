import asyncio
import logging
import os
from typing import Callable, Dict

from paho.mqtt.client import Client, MQTTMessage

from src.crud import get_device_by_id
from src.dependencies import redis_event_loop
from src.models.device import Device as DeviceModel
from src.plugins import PluginsManager
from src.schemas.device import (
    DeviceReceived as DeviceReceivedSchema,
    DeviceFrontend as DeviceFrontendSchema,
)
from src.streams.send import send_to_ws_service


logger = logging.getLogger(os.environ.get("LOGGER", "mqtt"))


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
    except ValueError:
        logger.error('Received invalid payload: "%s"' % payload)
        return

    try:
        device_type_name = payload.split(",")[1]
    except IndexError:
        device_type_name = ""

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
    except Exception as e:
        logger.error(e)
        return

    primary_device = get_device_by_id(mqtt_id)
    # Store client data in DB
    if primary_device is None:
        primary_device = DeviceManager().create_device(device_received_schema)
    else:
        primary_device = DeviceManager().update_device(device_received_schema)
    if not isinstance(primary_device, DeviceModel):
        logger.error(f"{primary_device=} is not a DeviceModel")
        return None

    device_frontend_schema = DeviceFrontendSchema(
        mqtt_id=mqtt_id,
        remote_name=device_received_schema.remote_name,
        name=primary_device.name,
        device_type_name=device_type_name,
        tags=[t.id for t in primary_device.tags],
        reboots=primary_device.reboots,
        last_seen=str(primary_device.last_seen) if primary_device.last_seen else None,
        last_update_sent=(
            str(primary_device.last_update_sent)
            if primary_device.last_update_sent
            else None
        ),
        plugin=device_received_schema.plugin,
    )

    # Schedule the coroutine on the main event loop from the MQTT thread
    if redis_event_loop.get() is not None:
        try:
            asyncio.run_coroutine_threadsafe(
                send_to_ws_service(device_frontend_schema), redis_event_loop.get()
            )
        except Exception as e:
            logger.error(
                "Error scheduling coroutine on redis streams event loop: %s" % e
            )
    else:
        logger.warning("Redis streams event loop not set. Cannot send message.")

    return device_frontend_schema
