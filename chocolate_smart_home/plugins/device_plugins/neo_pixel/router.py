import logging
from typing import Tuple

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from .crud import (
    delete_neo_pixel_device,
    get_all_neo_pixel_devices_data,
    get_neo_pixel_device_by_device_id,
    publish_message,
)
from .model import NeoPixel
from .schemas import NeoPixelDevice, NeoPixelDevices
from .utils import to_neo_pixel_schema


logger = logging.getLogger()
plugin_router = APIRouter(prefix="/neo_pixel")


@plugin_router.get("/")
def get_devices() -> Tuple[NeoPixelDevice, ...]:
    try:
        return tuple(map(to_neo_pixel_schema, get_all_neo_pixel_devices_data()))
    except SQLAlchemyError as e:
        (detail,) = e.args
        logger.error(detail)
        raise HTTPException(status_code=404, detail=detail)


@plugin_router.get("/{neo_pixel_device_id}")
def get_device(neo_pixel_device_id: int) -> NeoPixelDevice:
    try:
        neo_pixel_device: NeoPixel = get_neo_pixel_device_by_device_id(neo_pixel_device_id)
    except SQLAlchemyError as e:
        (detail,) = e.args
        logger.error(detail)
        raise HTTPException(status_code=404, detail=detail)
    return to_neo_pixel_schema(neo_pixel_device)


@plugin_router.post("/", response_model=None, status_code=204)
def update_devices(data: NeoPixelDevices):
    """Publish new "on" value to multiple devices."""
    for neo_pixel_device_id in data.ids:
        publish_message(neo_pixel_device_id=neo_pixel_device_id, on=data.on)


@plugin_router.post("/{neo_pixel_device_id}/{on_value}", response_model=None, status_code=204)
def update_device(neo_pixel_device_id: int, on_value: bool):
    """Publish new "on" value to single device."""
    publish_message(neo_pixel_device_id=neo_pixel_device_id, on=on_value)


@plugin_router.delete("/{neo_pixel_device_id}", response_model=None, status_code=204)
def delete_device(neo_pixel_device_id: int):
    try:
        delete_neo_pixel_device(neo_pixel_device_id)
    except SQLAlchemyError as e:
        (detail,) = e.args
        logger.error(detail)
        raise HTTPException(status_code=404, detail=detail)