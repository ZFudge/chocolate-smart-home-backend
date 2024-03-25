from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from chocolate_smart_home import crud, dependencies, schemas


router = APIRouter()


@router.get("/")
async def root():
    return {}


@router.get("/get_devices_data/", response_model=list[schemas.Device])
async def get_devices_data(db: Session = Depends(dependencies.get_db)):
    return crud.get_devices_data(db=db)


@router.patch("/update_devices_data/", response_model=list[schemas.Device])
async def update_devices_data(
    devices_data: list[schemas.DeviceUpdate], db: Session = Depends(dependencies.get_db)
) -> list[schemas.Device]:
    return crud.update_devices_data(db=db, devices_data=devices_data)


@router.get("/get_spaces_data/", response_model=list[schemas.Space])
async def get_spaces_data(db: Session = Depends(dependencies.get_db)):
    return crud.get_spaces_data(db=db)
