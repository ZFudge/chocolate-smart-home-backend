from typing import Tuple

from fastapi import APIRouter, HTTPException
from paho.mqtt import MQTTException
from sqlalchemy.exc import NoResultFound
from starlette.responses import JSONResponse

from src import crud, mqtt, schemas
import src.schemas.utils as schema_utils
from src.models import Device as models_Device
from src.websocket.dynamic_broadcast import dynamic_broadcast

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


@device_router.put("/{mqtt_id}/tags", response_model=schemas.Device)
async def put_device_tags(mqtt_id: int, tag_ids: schemas.TagIds):
    try:
        device: models_Device = crud.put_device_tags(mqtt_id, tag_ids.ids)
    except NoResultFound as e:
        (detail,) = e.args
        raise HTTPException(status_code=500, detail=detail)

    await dynamic_broadcast(device)

    if tag_ids.ids and len(device.tags) < len(tag_ids.ids):
        return JSONResponse(
            status_code=202,
            content={
                "detail": "Some tag ids were added. Of the given tag ids, %s, the following were not added: %s"
                % (
                    tag_ids.ids,
                    list(set(tag_ids.ids) - set([tag.id for tag in device.tags])),
                ),
                "device": schema_utils.to_schema(device).model_dump(),
            },
        )
    return schema_utils.to_schema(device)


@device_router.post("/tag/{device_id}/{tag_id}", response_model=schemas.Device)
def add_device_tag(device_id: int, tag_id: int):
    try:
        device = crud.add_device_tag(device_id, tag_id)
    except NoResultFound as e:
        (detail,) = e.args
        raise HTTPException(status_code=500, detail=detail)
    return schema_utils.to_schema(device)


@device_router.delete("/tag/{device_id}/{tag_id}", response_model=schemas.DeviceBase)
def remove_device_tag(device_id: int, tag_id: int):
    try:
        updated_device = crud.remove_device_tag(device_id, tag_id)
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


@device_router.post("/{mqtt_id}/name", response_model=schemas.Device)
async def update_device_name(mqtt_id: int, name: schemas.UpdateDeviceName):
    try:
        updated_device = crud.update_device_name(mqtt_id, name.name)
    except NoResultFound as e:
        (detail,) = e.args
        raise HTTPException(status_code=500, detail=detail)

    await dynamic_broadcast(updated_device)

    return schema_utils.to_schema(updated_device)


@device_router.get("/health/check/", response_model=dict[str, str], status_code=200)
def health() -> dict:
    return {"status": "ok"}
