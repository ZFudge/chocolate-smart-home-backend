import logging
import datetime as dt

from sqlalchemy.orm import Session

from src.crud import get_device_by_id, get_device_type_by_name, create_device_type
from src.models import Device as models_Device, DeviceType as models_DeviceType
from src.dependencies import db_session
from src.schemas import DeviceReceived as DeviceReceivedSchema


logger = logging.getLogger()


class BaseDeviceManager:
    def create_device(self, device: DeviceReceivedSchema) -> models_Device:
        logger.info('Creating Base device "%s"' % device)
        device_type_name: str = device.device_type_name
        device_type: models_DeviceType = get_device_type_by_name(
            device_type_name
        ) or create_device_type(device_type_name)
        # TODO: lookup existing device name from previously exported settings
        truncated_remote_name = device.remote_name.split(" - ")[0]
        db_device = models_Device(
            mqtt_id=device.mqtt_id,
            remote_name=device.remote_name,
            name=truncated_remote_name,
            device_type=device_type,
            last_seen=dt.datetime.now(),
        )
        db: Session = db_session.get()
        db.add(db_device)
        try:
            db.commit()
        except:
            db.rollback()
            raise
        db.refresh(db_device)
        return db_device

    def update_device(self, device: DeviceReceivedSchema, *_) -> models_Device:
        logger.info('Updating Base device "%s"' % device)
        db: Session = db_session.get()
        db_device: models_Device = get_device_by_id(device.mqtt_id)
        if db_device is None:
            raise ValueError(f"Device with mqtt_id {device.mqtt_id} not found")

        if device.device_type_name != db_device.device_type.name:
            logger.warning(f"Device with mqtt_id {device.mqtt_id} has a different device type: {db_device.device_type.name} -> {device.device_type_name}")
            device_type: models_DeviceType = get_device_type_by_name(
                device.device_type_name
            ) or create_device_type(device.device_type_name)
            db_device.device_type = device_type

        if db_device.remote_name != device.remote_name:
            db_device.reboots += 1
            db_device.remote_name = device.remote_name

        db_device.last_seen = dt.datetime.now()
        db.add(db_device)
        try:
            db.commit()
        except:
            db.rollback()
            raise
        db.refresh(db_device)
        return db_device

    def get_device_by_id(self, mqtt_id: int) -> models_Device | None:
        return get_device_by_id(mqtt_id)

    # def update_server_side_values(self, *_, **__):
    #     pass
