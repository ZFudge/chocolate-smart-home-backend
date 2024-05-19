import logging
from typing import Dict

import chocolate_smart_home.models as models
from chocolate_smart_home.dependencies import db_session
from chocolate_smart_home.plugins.base_device_manager import BaseDeviceManager
from .model import OnOffDevice


logger = logging.getLogger()

class OnOffDeviceManager(BaseDeviceManager):
    def create_device(self, device_data: Dict) -> OnOffDevice:
        logger.info('Creating device "%s"' % device_data)
        db = db_session.get()

        base_device: models.Device = super().create_device(device_data)
        new_on_off_device = OnOffDevice(on=device_data["on"], device=base_device)

        db.add(base_device)
        db.add(new_on_off_device)

        try:
            db.commit()
        except:
            db.rollback()
            raise

        db.refresh(new_on_off_device)
        return new_on_off_device

    def update_device(self, device_data: Dict) -> OnOffDevice:
        logger.info('Updating device "%s"' % device_data)
        db = db_session.get()

        base_device: models.Device = super().update_device(device_data)

        on_off_device = db.query(
            OnOffDevice
        ).filter(OnOffDevice.device == base_device).one()

        db.add(base_device)
        db.add(on_off_device)

        try:
            db.commit()
        except:
            db.rollback()
            raise

        db.refresh(on_off_device)
        return on_off_device


# Alias OnOffDeviceManager for use in ..discovered_plugins.DISCOVERED_PLUGINS["on_off"] dict
DeviceManager = OnOffDeviceManager
