import logging
from typing import Tuple

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError

import chocolate_smart_home.plugins.device_plugins.neo_pixel.crud as crud
import chocolate_smart_home.plugins.device_plugins.neo_pixel.model as model
import chocolate_smart_home.plugins.device_plugins.neo_pixel.schemas as schemas
from .utils import to_neo_pixel_schema


logger = logging.getLogger()
plugin_router = APIRouter(prefix="/neo_pixel")


@plugin_router.get("/")
def get_devices() -> Tuple[schemas.NeoPixelDevice, ...]:
    try:
        return tuple(map(to_neo_pixel_schema, crud.get_all_neo_pixel_devices_data()))
    except SQLAlchemyError as e:
        (detail,) = e.args
        logger.error(detail)
        raise HTTPException(status_code=404, detail=detail)


@plugin_router.get("/{neo_pixel_device_id}")
def get_device(neo_pixel_device_id: int) -> schemas.NeoPixelDevice:
    try:
        neo_pixel_device: model.NeoPixel = crud.get_neo_pixel_device_by_device_id(neo_pixel_device_id)
    except SQLAlchemyError as e:
        (detail,) = e.args
        logger.error(detail)
        raise HTTPException(status_code=404, detail=detail)
    return to_neo_pixel_schema(neo_pixel_device)


@plugin_router.post("/", response_model=None, status_code=204)
def update_devices(neo_pixel_data: schemas.NeoPixelDevices):
    """Publish new values to multiple Neo Pixel devices."""
    for neo_pixel_device_id in neo_pixel_data.ids:
        crud.publish_message(neo_pixel_device_id=neo_pixel_device_id, data=neo_pixel_data.data)


@plugin_router.post("/{neo_pixel_device_id}", response_model=None, status_code=204)
def update_device(neo_pixel_device_id: int, data: schemas.NeoPixelOptions):
    """Publish new values to a single Neo Pixel device."""
    crud.publish_message(neo_pixel_device_id=neo_pixel_device_id, data=data)


@plugin_router.delete("/{neo_pixel_device_id}", response_model=None, status_code=204)
def delete_device(neo_pixel_device_id: int):
    try:
        crud.delete_neo_pixel_device(neo_pixel_device_id)
    except SQLAlchemyError as e:
        (detail,) = e.args
        logger.error(detail)
        raise HTTPException(status_code=404, detail=detail)
