import logging
from typing import List

from sqlalchemy.orm import Session

import src.models as models
from src.dependencies import db_session
from src.plugins.base_device_manager import BaseDeviceManager
from .model import OnOff
from .schemas import OnOffDeviceReceived


logger = logging.getLogger()


class OnOffDeviceManager(BaseDeviceManager):
    """Manage "on_offs" and "devices" table rows using incoming device data."""

    def get_devices_by_mqtt_id(self, mqtt_id: int | List[int]) -> OnOff:
        db: Session = db_session.get()
        if isinstance(mqtt_id, list):
            return db.query(OnOff).filter(OnOff.device.has(models.Device.mqtt_id.in_(mqtt_id))).all()
        return db.query(OnOff).filter(OnOff.device.has(models.Device.mqtt_id == mqtt_id)).one()

    def create_device(self, on_off_device: OnOffDeviceReceived) -> OnOff:
        logger.info('Creating device "%s"' % on_off_device)
        db = db_session.get()

        device: models.Device = super().create_device(on_off_device.device)
        new_db_on_off = OnOff(on=on_off_device.on, device=device)

        db.add(new_db_on_off)

        try:
            db.commit()
        except:
            db.rollback()
            raise

        db.refresh(new_db_on_off)
        return new_db_on_off

    def update_device(self, on_off_device: OnOffDeviceReceived) -> OnOff:
        logger.info('Updating device "%s"' % on_off_device)
        db = db_session.get()

        device: models.Device = super().update_device(on_off_device.device)

        db_on_off = db.query(OnOff).filter(OnOff.device == device).one()

        db_on_off.on = on_off_device.on

        db.add(device)
        db.add(db_on_off)

        try:
            db.commit()
        except:
            db.rollback()
            raise

        db.refresh(db_on_off)
        return db_on_off


# Alias OnOffDeviceManager for use in ..discovered_plugins.DISCOVERED_PLUGINS["on_off"] dict
DeviceManager = OnOffDeviceManager
