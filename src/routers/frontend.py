from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src import crud, dependencies, schemas


router = APIRouter()


@router.post("/create_device_type", response_model=schemas.DeviceType)
def create_device_type(
    device_type: schemas.DeviceTypeBase, db: Session = Depends(dependencies.get_db)
):
    try:
        return crud.create_device_type(db, device_type.name)
    except IntegrityError as e:
        raise HTTPException(status_code=500, detail=e.orig.diag.message_detail)
