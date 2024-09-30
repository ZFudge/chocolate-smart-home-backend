import logging

import chocolate_smart_home.models as models
from chocolate_smart_home.dependencies import db_session
from chocolate_smart_home.plugins.base_device_manager import BaseDeviceManager
from .model import NeoPixel
from .schemas import NeoPixelDeviceReceived


logger = logging.getLogger()


class NeoPixelDeviceManager(BaseDeviceManager):
    """Manage "neo_pixels" and "devices" table rows using incoming device data."""

    def create_device(self, incoming_neo_pixel: NeoPixelDeviceReceived) -> NeoPixel:
        logger.info('Creating device "%s"' % incoming_neo_pixel)
        db = db_session.get()

        device: models.Device = super().create_device(incoming_neo_pixel.device)
        new_db_neo_pixel = NeoPixel(
            on=incoming_neo_pixel.on,
            twinkle=incoming_neo_pixel.twinkle,
            all_twinkle_colors_are_current=incoming_neo_pixel.all_twinkle_colors_are_current,
            transform=incoming_neo_pixel.transform,
            ms=incoming_neo_pixel.ms,
            brightness=incoming_neo_pixel.brightness,
            palette=incoming_neo_pixel.palette,
            device=device,
        )
        if incoming_neo_pixel.pir is not None:
            new_db_neo_pixel.pir_armed = incoming_neo_pixel.pir.armed
            new_db_neo_pixel.pir_timeout_seconds = incoming_neo_pixel.pir.timeout_seconds

        db.add(new_db_neo_pixel)

        try:
            db.commit()
        except:
            db.rollback()
            raise

        db.refresh(new_db_neo_pixel)
        return new_db_neo_pixel

    def update_device(self, incoming_neo_pixel: NeoPixelDeviceReceived) -> NeoPixel:
        logger.info('Updating device "%s"' % incoming_neo_pixel)
        db = db_session.get()

        device: models.Device = super().update_device(incoming_neo_pixel.device)

        db_neo_pixel = db.query(NeoPixel).filter(NeoPixel.device == device).one()

        db_neo_pixel.on = incoming_neo_pixel.on
        db_neo_pixel.twinkle = incoming_neo_pixel.twinkle
        db_neo_pixel.all_twinkle_colors_are_current = incoming_neo_pixel.all_twinkle_colors_are_current
        db_neo_pixel.transform = incoming_neo_pixel.transform
        db_neo_pixel.ms = incoming_neo_pixel.ms
        db_neo_pixel.brightness = incoming_neo_pixel.brightness
        db_neo_pixel.palette = incoming_neo_pixel.palette
        if incoming_neo_pixel.pir is not None:
            db_neo_pixel.pir_armed = incoming_neo_pixel.pir.armed
            db_neo_pixel.pir_timeout_seconds = incoming_neo_pixel.pir.timeout_seconds

        db.add(device)
        db.add(db_neo_pixel)

        try:
            db.commit()
        except:
            db.rollback()
            raise

        db.refresh(db_neo_pixel)
        return db_neo_pixel


# Alias NeoPixelDeviceManager for use in ..discovered_plugins.DISCOVERED_PLUGINS["neo_pixel"] dict
DeviceManager = NeoPixelDeviceManager
