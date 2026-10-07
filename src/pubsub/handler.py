import asyncio
import logging
import os

from paho.mqtt.client import Client, MQTTMessage

from src import crud, models, schemas
from src.dependencies import asyncio_event_loop
from src.plugins import PluginsManager
from src.streams.send import send_to_ws_service


logger = logging.getLogger(os.environ.get("LOGGER", "mqtt"))


def mqtt_message_handler(
    _client: Client,
    _userdata: None,
    message: MQTTMessage,
) -> schemas.DeviceReceived | None:
    if message.payload is None:
        return

    payload: str = message.payload.decode()
    logger.info('Message received from "%s": "%s"' % (message.topic, payload))

    try:
        mqtt_id: int = int(payload.split(",")[0])
    except ValueError:
        logger.error('Received invalid payload: "%s"' % payload)
        return
    # mark as seen as soon as we have a valid mqtt id
    db_primary_device: models.Device | None = crud.set_last_seen_to_current_time(
        mqtt_id
    )

    try:
        device_type_name = payload.split(",")[1]
    except IndexError:
        device_type_name = ""

    plugin: dict = PluginsManager.get_plugin_by_device_type_name(device_type_name)

    ControllerToServerMessenger: callable = plugin["ControllerToServerMessenger"]
    DeviceManager: callable = plugin["DeviceManager"]

    # Parse message data
    try:
        device_received_schema: schemas.DeviceReceived = (
            ControllerToServerMessenger().parse_controller_msg(payload)
        )
    except Exception as e:
        logger.error(e)
        return

    # Store client data in DB
    if db_primary_device is None:
        db_primary_device = DeviceManager().create_device(device_received_schema)
    else:
        db_primary_device = DeviceManager().update_device(device_received_schema)
    if not isinstance(db_primary_device, models.Device):
        logger.error(
            f"Received instance of {type(db_primary_device).__name__}, {db_primary_device}, instead of models.Device object"
        )
        return None

    device_frontend_schema = schemas.DeviceFrontend(
        mqtt_id=mqtt_id,
        remote_name=device_received_schema.remote_name,
        name=db_primary_device.name,
        device_type_name=device_type_name,
        reboots=db_primary_device.reboots,
        tags=[t.id for t in db_primary_device.tags],
        last_seen=(
            str(db_primary_device.last_seen) if db_primary_device.last_seen else None
        ),
        last_update_sent=(
            str(db_primary_device.last_update_sent)
            if db_primary_device.last_update_sent
            else None
        ),
        plugin=device_received_schema.plugin,
    )

    # Schedule the coroutine on the main event loop from the MQTT thread
    if asyncio_event_loop.get() is not None:
        try:
            asyncio.run_coroutine_threadsafe(
                send_to_ws_service(device_frontend_schema), asyncio_event_loop.get()
            )
        except Exception as e:
            logger.error(
                "Error scheduling coroutine on redis streams event loop: %s" % e
            )
    else:
        logger.warning("Redis streams event loop not set. Cannot send message.")

    return device_frontend_schema
