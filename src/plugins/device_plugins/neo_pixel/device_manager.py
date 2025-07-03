import logging
from typing import List

from sqlalchemy.orm import Session

import src.models as models
from src.crud.devices import get_devices_by_mqtt_id
from src.dependencies import db_session
from src.plugins.base_device_manager import BaseDeviceManager
from .model import NeoPixel
from .schemas import NeoPixelDeviceReceived, NeoPixelOptions


logger = logging.getLogger()


class NeoPixelDeviceManager(BaseDeviceManager):
    """Manage "neo_pixels" and "devices" table rows using incoming device data."""

    # These values are only used server-side and not sent to the controller.
    SERVER_SIDE_VALUES = [
        "scheduled_palette_rotation",
    ]

    def get_devices_by_mqtt_id(self, mqtt_id: int | List[int]) -> NeoPixel:
        db: Session = db_session.get()
        if isinstance(mqtt_id, list):
            return db.query(NeoPixel).filter(NeoPixel.device.has(models.Device.mqtt_id.in_(mqtt_id))).all()
        return db.query(NeoPixel).filter(NeoPixel.device.has(models.Device.mqtt_id == mqtt_id)).one()

    def create_device(self, incoming_neo_pixel: NeoPixelDeviceReceived) -> NeoPixel:
        logger.info('Creating Neo Pixel device "%s"' % incoming_neo_pixel)
        db = db_session.get()

        device: models.Device = super().create_device(incoming_neo_pixel.device)
        new_db_neo_pixel = NeoPixel(
            on=incoming_neo_pixel.on,
            twinkle=incoming_neo_pixel.twinkle,
            transform=incoming_neo_pixel.transform,
            ms=incoming_neo_pixel.ms,
            brightness=incoming_neo_pixel.brightness,
            palette=incoming_neo_pixel.palette,
            device=device,
        )
        if incoming_neo_pixel.pir is not None:
            new_db_neo_pixel.armed = incoming_neo_pixel.pir.armed
            new_db_neo_pixel.timeout = (
                incoming_neo_pixel.pir.timeout
            )

        db.add(new_db_neo_pixel)

        try:
            db.commit()
        except:
            db.rollback()
            raise

        db.refresh(new_db_neo_pixel)
        return new_db_neo_pixel

    def update_device(self, incoming_neo_pixel: NeoPixelDeviceReceived) -> NeoPixel:
        logger.info('Updating Neo Pixel device "%s"' % incoming_neo_pixel)
        db = db_session.get()

        device: models.Device = super().update_device(incoming_neo_pixel.device)

        db_neo_pixel = db.query(NeoPixel).filter(NeoPixel.device == device).one()

        db_neo_pixel.on = incoming_neo_pixel.on
        # START twinkle
        db_neo_pixel.twinkle = incoming_neo_pixel.twinkle
        db_neo_pixel.all_twinkle_colors_are_current = (
            incoming_neo_pixel.all_twinkle_colors_are_current
        )
        # END twinkle
        db_neo_pixel.transform = incoming_neo_pixel.transform
        db_neo_pixel.ms = incoming_neo_pixel.ms
        db_neo_pixel.brightness = incoming_neo_pixel.brightness
        db_neo_pixel.palette = incoming_neo_pixel.palette
        if incoming_neo_pixel.pir is not None:
            db_neo_pixel.armed = incoming_neo_pixel.pir.armed
            db_neo_pixel.timeout = incoming_neo_pixel.pir.timeout

        db.add(device)
        db.add(db_neo_pixel)

        try:
            db.commit()
        except:
            db.rollback()
            raise

        db.refresh(db_neo_pixel)
        return db_neo_pixel

    def update_server_side_values(
        self, incoming_neo_pixel: dict | NeoPixelOptions
    ) -> List[NeoPixel]:
        logger.info(
            'Updating server side values for Neo Pixel device "%s"' % incoming_neo_pixel
        )
        db = db_session.get()
        if isinstance(incoming_neo_pixel, NeoPixelOptions):
            incoming_neo_pixel = incoming_neo_pixel.model_dump()

        np_db_devices = []
        value_name = incoming_neo_pixel.name
        value = incoming_neo_pixel.value
        mqtt_ids = incoming_neo_pixel.get_mqtt_ids()
        for mqtt_id in mqtt_ids:
            db_device: models.Device = get_devices_by_mqtt_id(mqtt_id)
            db_neo_pixel = db.query(NeoPixel).filter(NeoPixel.device == db_device).one()

            if value_name == "scheduled_palette_rotation":
                db_neo_pixel.scheduled_palette_rotation = value

            db.add(db_neo_pixel)
            np_db_devices.append(db_neo_pixel)

        try:
            db.commit()
        except:
            db.rollback()
            raise

        return np_db_devices


# Alias NeoPixelDeviceManager for use in ..discovered_plugins.DISCOVERED_PLUGINS["neo_pixel"] dict
DeviceManager = NeoPixelDeviceManager
