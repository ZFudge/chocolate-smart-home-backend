import logging
from typing import Dict

import chocolate_smart_home.models as models
from chocolate_smart_home.dependencies import db_session
from chocolate_smart_home.plugins.base_device_manager import BaseDeviceManager
from .model import NeoPixel


logger = logging.getLogger()


class NeoPixelDeviceManager(BaseDeviceManager):
    """Manage "neo_pixels" and "devices" table rows using incoming device data."""

    def create_device(self, device_data: Dict) -> NeoPixel:
        logger.info('Creating device "%s"' % device_data)
        db = db_session.get()

        device: models.Device = super().create_device(device_data)
        new_neo_pixel = NeoPixel(on=device_data["on"], device=device)

        db.add(new_neo_pixel)

        try:
            db.commit()
        except:
            db.rollback()
            raise

        db.refresh(new_neo_pixel)
        return new_neo_pixel

    def update_device(self, device_data: Dict) -> NeoPixel:
        logger.info('Updating device "%s"' % device_data)
        db = db_session.get()

        device: models.Device = super().update_device(device_data)

        neo_pixel = db.query(NeoPixel).filter(NeoPixel.device == device).one()

        neo_pixel.on = device_data["on"]

        db.add(device)
        db.add(neo_pixel)

        try:
            db.commit()
        except:
            db.rollback()
            raise

        db.refresh(neo_pixel)
        return neo_pixel


# Alias NeoPixelDeviceManager for use in ..discovered_plugins.DISCOVERED_PLUGINS["neo_pixel"] dict
DeviceManager = NeoPixelDeviceManager
