import logging
from typing import List

from sqlalchemy.orm import Session

import src.crud.device_types as device_types
import src.models as models
from src.crud.devices import get_device_by_mqtt_id
from src.dependencies import db_session
from src.schemas import DeviceReceived


logger = logging.getLogger()


class BaseDeviceManager:
    def create_device(self, device: DeviceReceived) -> models.Device:
        logger.info('Creating Base device "%s"' % device)

        device_type_name: str = device.device_type_name
        device_type: models.DeviceType = (
            device_types.get_new_or_existing_device_type_by_name(device_type_name)
        )

        truncated_remote_name = device.remote_name.split(" - ")[0]

        db_device = models.Device(
            online=True,
            mqtt_id=device.mqtt_id,
            remote_name=device.remote_name,
            name=truncated_remote_name,
            device_type=device_type,
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

    def update_device(self, device: DeviceReceived) -> models.Device:
        logger.info('Updating Base device "%s"' % device)
        db: Session = db_session.get()

        db_device: models.Device = get_device_by_mqtt_id(device.mqtt_id)

        device_type_name: str = device.device_type_name
        device_type: models.DeviceType = (
            device_types.get_new_or_existing_device_type_by_name(device_type_name)
        )

        truncated_remote_name = device.remote_name.split(" - ")[0]
        db_device.name = truncated_remote_name

        if db_device.remote_name != device.remote_name:
            db_device.reboots += 1
        db_device.remote_name = device.remote_name

        db_device.device_type = device_type
        db_device.online = True

        db.add(db_device)

        try:
            db.commit()
        except:
            db.rollback()
            raise

        db.refresh(db_device)
        return db_device
