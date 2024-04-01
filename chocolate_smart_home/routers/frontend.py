from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from chocolate_smart_home import dependencies
import chocolate_smart_home.crud as crud
import chocolate_smart_home.schemas as schemas


router = APIRouter()


@router.get("/")
async def root():
    return {}


@router.get("/get_devices_data/", response_model=list[schemas.Device])
async def get_devices_data(db: Session = Depends(dependencies.get_db)):
    return crud.get_devices_data(db=db)


@router.patch("/update_devices_data/",
              response_model=list[schemas.DeviceUpdate])
async def update_devices_data(
    devices_data: list[schemas.DeviceUpdate],
    db: Session = Depends(dependencies.get_db)
) -> list[schemas.Device]:
    return crud.update_devices_data(devices_data=devices_data, db=db)


@router.get("/get_spaces_data/", response_model=list[schemas.Space])
async def get_spaces_data(db: Session = Depends(dependencies.get_db)):
    return crud.get_spaces_data(db=db)


@router.post("/create_device_type/", response_model=schemas.DeviceType)
def create_device_type(device_type: schemas.DeviceTypeBase,
                       db: Session = Depends(dependencies.get_db)):
    return crud.create_device_type(db, device_type.name)


@router.post("/create_device/", response_model=schemas.Device)
def create_device(device: schemas.DeviceReceived,
                  db: Session = Depends(dependencies.get_db)):
    new_device = crud.create_device(db, device)
    return schemas.Device(
        id=new_device.id,
        mqtt_id=new_device.mqtt_id,
        device_type=schemas.DeviceType(id=new_device.device_type.id,
                                       name=new_device.device_type.name),
        name=new_device.name,
        remote_name=new_device.remote_name,
        online=new_device.online
    )
