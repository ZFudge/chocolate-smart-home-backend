from functools import singledispatch

from sqlalchemy.orm import Session

from chocolate_smart_home import models
from chocolate_smart_home.dependencies import db_session
import chocolate_smart_home.schemas as schemas


@singledispatch
def create_device_type(db: Session,
                       device_type_name: str) -> schemas.DeviceType:
    db_device_type = models.DeviceType(name=device_type_name)
    db.add(db_device_type)
    db.commit()
    db.refresh(db_device_type)
    return db_device_type


@create_device_type.register
def _(device_type_name: str):
    return create_device_type(db_session.get(), device_type_name)


def get_device_type_by_name(device_type_name: schemas.DeviceTypeBase):
    db = db_session.get()
    device_type = db.query(models.DeviceType).filter(
        models.DeviceType.name == device_type_name
    ).first()
    if device_type is None:
        return create_device_type(db, device_type_name)
    return device_type
