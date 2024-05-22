import logging
from typing import Dict

import chocolate_smart_home.models as models
from chocolate_smart_home.dependencies import db_session
from chocolate_smart_home.plugins.base_device_manager import BaseDeviceManager
from .model import OnOff


logger = logging.getLogger()

class OnOffDeviceManager(BaseDeviceManager):
    """Manage "on_offs" and "devices" table rows using incoming device data."""

    def create_device(self, device_data: Dict) -> OnOff:
        logger.info("Creating device \"%s\"" % device_data)
        db = db_session.get()

        device: models.Device = super().create_device(device_data)
        new_on_off = OnOff(on=device_data["on"], device=device)

        db.add(device)
        db.add(new_on_off)

        try:
            db.commit()
        except:
            db.rollback()
            raise

        db.refresh(new_on_off)
        return new_on_off

    def update_device(self, device_data: Dict) -> OnOff:
        logger.info("Updating device \"%s\"" % device_data)
        db = db_session.get()

        device: models.Device = super().update_device(device_data)

        on_off = db.query(OnOff).filter(OnOff.device == device).one()

        on_off.on = device_data["on"]

        db.add(device)
        db.add(on_off)

        try:
            db.commit()
        except:
            db.rollback()
            raise

        db.refresh(on_off)
        return on_off


# Alias OnOffDeviceManager for use in ..discovered_plugins.DISCOVERED_PLUGINS["on_off"] dict
DeviceManager = OnOffDeviceManager
