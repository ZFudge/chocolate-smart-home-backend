from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session

from chocolate_smart_home import crud, dependencies, models, schemas


router = APIRouter()


@router.post("/create_device_type", response_model=schemas.DeviceType)
def create_device_type(
    device_type: schemas.DeviceTypeBase, db: Session = Depends(dependencies.get_db)
):
    try:
        return crud.create_device_type(db, device_type.name)
    except IntegrityError as e:
        raise HTTPException(status_code=500, detail=e.orig.diag.message_detail)


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
