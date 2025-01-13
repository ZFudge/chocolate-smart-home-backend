from typing import Tuple

from fastapi import APIRouter, HTTPException
from paho.mqtt import MQTTException
from sqlalchemy.exc import NoResultFound

from chocolate_smart_home import crud, mqtt, schemas
import chocolate_smart_home.schemas.utils as schema_utils


device_router = APIRouter(prefix="/device")


@device_router.get("/", response_model=Tuple[schemas.Device, ...])
def get_devices_data():
    devices_data = crud.get_all_devices_data()
    return tuple(map(schema_utils.to_schema, devices_data))


@device_router.get("/{device_id}", response_model=schemas.Device)
def get_device_data(device_id: int):
    try:
        device = crud.get_device_by_device_id(device_id)
        return schema_utils.to_schema(device)
    except NoResultFound:
        detail = f"No Device with an id of {device_id} found."
        raise HTTPException(status_code=404, detail=detail)


@device_router.delete("/{device_id}", response_model=None, status_code=204)
def delete_device(device_id: int):
    try:
        crud.delete_device(device_id)
    except NoResultFound as e:
        (detail,) = e.args
        raise HTTPException(status_code=500, detail=detail)


@device_router.post("/space/{device_id}", response_model=schemas.Device)
def add_device_space(device_id: int, space: schemas.SpaceId):
    try:
        device = crud.add_device_space(device_id, space.id)
    except NoResultFound as e:
        (detail,) = e.args
        raise HTTPException(status_code=500, detail=detail)
    return schema_utils.to_schema(device)


@device_router.delete("/space/{device_id}", response_model=schemas.DeviceBase)
def remove_device_space(device_id: int):
    try:
        updated_device = crud.remove_device_space(device_id)
    except NoResultFound as e:
        (detail,) = e.args
        raise HTTPException(status_code=500, detail=detail)
    return schema_utils.to_schema(updated_device)


@device_router.head(
    "/broadcast_request_devices_state/", response_model=None, status_code=204
)
def broadcast_request_devices_state():
    try:
        mqtt.mqtt_client_ctx.get().request_all_devices_data()
    except MQTTException as e:
        (detail,) = e.args
        raise HTTPException(status_code=500, detail=detail)
