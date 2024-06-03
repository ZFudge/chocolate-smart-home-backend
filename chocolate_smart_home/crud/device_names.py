import logging

from functools import singledispatch

from sqlalchemy.orm import Session

from chocolate_smart_home import models
from chocolate_smart_home.dependencies import db_session
import chocolate_smart_home.schemas as schemas


logger = logging.getLogger()


def update_device_name(device_name_new_name: schemas.DeviceNameUpdate) -> models.DeviceName:
    db = db_session.get()
    db_device_name = (
        db.query(models.DeviceName)
        .filter(models.DeviceName.id == device_name_new_name.id)
        .one()
    )
    if db_device_name.name == device_name_new_name.name:
        return db_device_name

    device = (
        db.query(models.Device)
        .filter(models.Device.device_name_id == device_name_new_name.id)
        .one()
    )

    truncated_remote_name = device.remote_name.split(" - ")[0]
    if device_name_new_name.name == truncated_remote_name:
        db_device_name.is_server_side_name = False
    else:
        db_device_name.is_server_side_name = True
    
    db_device_name.name = device_name_new_name.name

    db.add(db_device_name)

    try:
        db.commit()
    except:
        db.rollback()
        raise

    db.refresh(db_device_name)
    return db_device_name
