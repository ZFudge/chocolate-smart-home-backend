import logging
from typing import Tuple

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from .crud import (
    delete_on_off_device,
    get_all_on_off_devices_data,
    get_on_off_device_by_device_id,
    publish_message,
)
from .model import OnOff
from .schemas import OnOffDevice, OnOffDevices
from .utils import to_on_off_schema


logger = logging.getLogger()
plugin_router = APIRouter(prefix="/on_off")


@plugin_router.get("/")
def get_devices() -> Tuple[OnOffDevice, ...]:
    try:
        return tuple(map(to_on_off_schema, get_all_on_off_devices_data()))
    except SQLAlchemyError as e:
        (detail,) = e.args
        logger.error(detail)
        raise HTTPException(status_code=404, detail=detail)


@plugin_router.get("/{on_off_device_id}")
def get_device(on_off_device_id: int) -> OnOffDevice:
    try:
        on_off_device: OnOff = get_on_off_device_by_device_id(on_off_device_id)
    except SQLAlchemyError as e:
        (detail,) = e.args
        logger.error(detail)
        raise HTTPException(status_code=404, detail=detail)
    return to_on_off_schema(on_off_device)


@plugin_router.post("/", response_model=None, status_code=204)
def update_devices(data: OnOffDevices):
    """Publish new "on" value to multiple devices."""
    for on_off_device_id in data.mqtt_ids:
        publish_message(on_off_device_id=on_off_device_id, on=data.on)


@plugin_router.post(
    "/{on_off_device_id}/{on_value}", response_model=None, status_code=204
)
def update_device(on_off_device_id: int, on_value: bool):
    """Publish new "on" value to single device."""
    publish_message(on_off_device_id=on_off_device_id, on=on_value)


@plugin_router.delete("/{on_off_device_id}", response_model=None, status_code=204)
def delete_device(on_off_device_id: int):
    try:
        delete_on_off_device(on_off_device_id)
    except SQLAlchemyError as e:
        (detail,) = e.args
        logger.error(detail)
        raise HTTPException(status_code=404, detail=detail)
