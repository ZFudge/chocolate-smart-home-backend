import logging
from typing import Dict

from sqlalchemy.orm import Session

import chocolate_smart_home.crud.device_types as device_types
import chocolate_smart_home.models as models
from chocolate_smart_home.crud.devices import get_device_by_mqtt_id
from chocolate_smart_home.dependencies import db_session

logger = logging.getLogger()

class BaseDeviceManager:
    def create_device(self, device_data: Dict) -> models.Device:
        logger.info('Creating device "%s"' % device_data)

        device_type_name: str = device_data["device_type_name"]
        device_type: models.DeviceType = device_types.get_new_or_existing_device_type_by_name(device_type_name)

        db_device = models.Device(
            mqtt_id=device_data["mqtt_id"],
            device_type=device_type,
            remote_name=device_data["remote_name"],
            name=device_data.get("name", ""),
            online=True,
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

    def update_device(self, device_data: Dict) -> models.Device:
        logger.info('Updating device "%s"' % device_data)

        device_type_name: str = device_data["device_type_name"]
        device_type: models.DeviceType = device_types.get_new_or_existing_device_type_by_name(device_type_name)

        device: models.Device = get_device_by_mqtt_id(device_data["mqtt_id"])

        if device.remote_name != device_data["remote_name"]:
            device.reboots += 1

        device.device_type = device_type
        device.remote_name = device_data["remote_name"]
        device.name = device_data.get("name", "")
        device.online = True

        db: Session = db_session.get()
        db.add(device)

        try:
            db.commit()
        except:
            db.rollback()
            raise

        db.refresh(device)
        return device
