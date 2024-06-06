from typing import Tuple

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session

from chocolate_smart_home import dependencies, models
import chocolate_smart_home.crud as crud
import chocolate_smart_home.schemas as schemas
import chocolate_smart_home.schemas.utils as schema_utils


router = APIRouter()


@router.post("/create_device_type", response_model=schemas.DeviceType)
def create_device_type(
    device_type: schemas.DeviceTypeBase, db: Session = Depends(dependencies.get_db)
):
    try:
        return crud.create_device_type(db, device_type.name)
    except IntegrityError as e:
        raise HTTPException(status_code=500, detail=e.orig.diag.message_detail)


@router.get("/get_device_data/{device_id}", response_model=schemas.Device)
def get_device_data(device_id: int):
    try:
        device = crud.get_device_by_device_id(device_id)

        return schema_utils.device_to_schema(device)
    except NoResultFound:
        detail = f"No device with an id of {device_id} found."
        raise HTTPException(status_code=404, detail=detail)


@router.get("/get_devices_data", response_model=Tuple[schemas.Device, ...])
def get_devices_data(db: Session = Depends(dependencies.get_db)):
    return tuple(map(schema_utils.device_to_schema, crud.get_all_devices_data(db)))


@router.delete("/delete_device/{device_id}", response_model=None, status_code=204)
def delete_device(device_id: int):
    try:
        crud.delete_device(Model=models.Device, device_id=device_id)
    except NoResultFound as e:
        (detail,) = e.args
        raise HTTPException(status_code=500, detail=detail)


@router.put("/update_device_name/{device_name_id}", response_model=schemas.DeviceName)
def update_device_name(device_name_id: int, device_name: schemas.DeviceNameUpdate):
    try:
        device_name: models.DeviceName = crud.update_device_name(device_name)
        return schemas.DeviceName(
            id=device_name.id,
            name=device_name.name,
            is_server_side_name=device_name.is_server_side_name,
        )
    except NoResultFound as e:
        (detail,) = e.args
        raise HTTPException(status_code=500, detail=detail)
