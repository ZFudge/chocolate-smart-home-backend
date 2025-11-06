import logging
from typing import Dict, Callable
from src.models import Device as models_Device, DeviceType as models_DeviceType
from src.dependencies import db_session
from sqlalchemy.orm import Session

from src.plugins.discovered_plugins import get_plugin_by_device_type
from src.websocket.connection_manager import manager

logger = logging.getLogger()


async def dynamic_broadcast(device: models_Device):
    if not manager.active_connections or not device or not device.device_type_id:
        return
    logger.info(f"dynamic_broadcast: Dynamic broadcasting device {device}")
    db: Session = db_session.get()
    device_type = (
        db.query(models_DeviceType)
        .filter(models_DeviceType.id == device.device_type_id)
        .first()
    )
    device_plugin: Dict = get_plugin_by_device_type(device_type.name)

    DuplexMessenger: Callable = device_plugin["DuplexMessenger"]
    DeviceManager: Callable = device_plugin["DeviceManager"]

    if hasattr(DuplexMessenger, "serialize_db_objects"):
        device_db_object = DeviceManager().get_devices_by_mqtt_id(device.mqtt_id)
        await manager.broadcast(
            DuplexMessenger().serialize_db_objects(device_db_object)
        )
    else:
        device_db_object = DeviceManager().get_devices_by_mqtt_id(device.mqtt_id)
        await manager.broadcast(DuplexMessenger().serialize(device_db_object))
