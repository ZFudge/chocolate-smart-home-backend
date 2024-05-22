import logging

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from .crud import delete_on_off_device, get_on_off_device_by_device_id, publish_update
from .model import OnOff
from .schemas import OnOffDeviceData, OnOffDevices
from .utils import on_off_device_to_full_device_data_schema


logger = logging.getLogger()
plugin_router = APIRouter(prefix="/on_off")

@plugin_router.get("/{on_off_device_id}")
def get_device(on_off_device_id: int) -> OnOffDeviceData:
    try:
        on_off_device: OnOff = get_on_off_device_by_device_id(on_off_device_id)
    except SQLAlchemyError as e:
        (detail,) = e.args
        logger.error(detail)
        raise HTTPException(status_code=404, detail=detail)
    return on_off_device_to_full_device_data_schema(on_off_device)


@plugin_router.post("/{on_off_device_id}/{on_value}", response_model=None, status_code=204)
def update_device(on_off_device_id: int, on_value: bool):
    """Publish new "on" value to single device."""
    publish_update(on_off_device_id=on_off_device_id, on=on_value)


@plugin_router.post("/", response_model=None, status_code=204)
def update_devices(data: OnOffDevices):
    """Publish new "on" value to multiple devices."""
    for on_off_device_id in data.ids:
        publish_update(on_off_device_id=on_off_device_id, on=data.on)


@plugin_router.delete("/{on_off_device_id}", response_model=None, status_code=204)
def delete_device(on_off_device_id: int):
    try:
        delete_on_off_device(on_off_device_id)
    except SQLAlchemyError as e:
        (detail,) = e.args
        logger.error(detail)
        raise HTTPException(status_code=404, detail=detail)
