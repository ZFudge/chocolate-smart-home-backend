from functools import singledispatch

from sqlalchemy.orm import Session

from chocolate_smart_home import models
from chocolate_smart_home.dependencies import db_session
import chocolate_smart_home.crud.device_types as device_types
import chocolate_smart_home.schemas as schemas


@singledispatch
def create_device(db: Session, device_data: schemas.DeviceReceived) -> schemas.Device:
    db_device = models.Device(
        mqtt_id=device_data.mqtt_id,
        device_type=device_types.get_device_type_by_name(device_data.device_type_name),
        remote_name=device_data.remote_name,
        name=device_data.name,
        online=True,
    )
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


@create_device.register
def _(mqtt_id: str, device_type_name: str, remote_name: str, name: str) -> schemas.Device:
    device_data = schemas.DeviceReceived(
        mqtt_id=mqtt_id,
        device_type_name=device_type_name,
        remote_name=remote_name,
        name=name,
    )
    return create_device(db_session.get(), device_data)


@singledispatch
def update_device(db: Session, device_data: schemas.DeviceBase):
    db_device = get_device_by_mqtt_id(device_data.mqtt_id)
    db_device.device_type = device_types.get_device_type_by_name(device_data.device_type_name)
    db_device.remote_name = device_data.remote_name
    db_device.name = device_data.name
    db_device.online = True
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


@update_device.register
def _(
    mqtt_id: str,
    device_type_name: str,
    remote_name: str,
    name: str,
    online: bool,
):
    device_data = schemas.DeviceBase(
        mqtt_id=mqtt_id,
        device_type_name=device_type_name,
        remote_name=remote_name,
        name=name,
        online=online
    )
    return update_device(db_session.get(), device_data)

def get_device_by_mqtt_id(mqtt_id: int):
    return db_session.get().query(models.Device).filter(
        models.Device.mqtt_id == mqtt_id
    ).first()
