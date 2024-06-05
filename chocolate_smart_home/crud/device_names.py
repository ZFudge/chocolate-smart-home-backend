import logging

from chocolate_smart_home import models
from chocolate_smart_home.dependencies import db_session
import chocolate_smart_home.schemas as schemas


logger = logging.getLogger()


def update_device_name(new_device_name_data: schemas.DeviceNameUpdate) -> models.DeviceName:
    db = db_session.get()

    device_name = (
        db.query(models.DeviceName)
        .filter(models.DeviceName.id == new_device_name_data.id)
        .one()
    )
    if device_name.name == new_device_name_data.name:
        return device_name

    truncated_remote_name = device_name.device.remote_name.split(" - ")[0]
    if new_device_name_data.name == truncated_remote_name:
        device_name.is_server_side_name = False
    else:
        device_name.is_server_side_name = True
    
    device_name.name = new_device_name_data.name

    db.add(device_name)

    try:
        db.commit()
    except:
        db.rollback()
        raise

    db.refresh(device_name)
    return device_name
