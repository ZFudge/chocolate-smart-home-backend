import logging
from typing import Dict

from sqlalchemy.orm import Session

import chocolate_smart_home.crud.device_types as device_types
import chocolate_smart_home.models as models
from chocolate_smart_home.crud.devices import get_device_by_mqtt_client_id
from chocolate_smart_home.dependencies import db_session

logger = logging.getLogger()


class BaseDeviceManager:
    def create_device(self, device_data: Dict) -> models.Device:
        logger.info('Creating device "%s"' % device_data)

        client = models.Client(mqtt_id=device_data["mqtt_id"])

        device_type_name: str = device_data["device_type_name"]
        device_type: models.DeviceType = (
            device_types.get_new_or_existing_device_type_by_name(device_type_name)
        )

        truncated_remote_name = device_data["remote_name"].split(" - ")[0]
        device_name = models.DeviceName(name=truncated_remote_name)

        db_device = models.Device(
            online=True,
            remote_name=device_data["remote_name"],
            client=client,
            device_type=device_type,
            device_name=device_name,
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
        db: Session = db_session.get()

        device: models.Device = get_device_by_mqtt_client_id(device_data["mqtt_id"])

        device_type_name: str = device_data["device_type_name"]
        device_type: models.DeviceType = (
            device_types.get_new_or_existing_device_type_by_name(device_type_name)
        )

        truncated_remote_name = device_data["remote_name"].split(" - ")[0]
        device_name = db.query(models.DeviceName).filter(models.DeviceName.id == device.device_name_id).one()
        device_name.name = truncated_remote_name

        if device.remote_name != device_data["remote_name"]:
            device.reboots += 1

        device.device_type = device_type
        device.device_name = device_name
        device.remote_name = device_data["remote_name"]
        device.online = True

        db.add(device_name)
        db.add(device)

        try:
            db.commit()
        except:
            db.rollback()
            raise

        db.refresh(device)
        return device
