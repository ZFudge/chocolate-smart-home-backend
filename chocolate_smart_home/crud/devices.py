import logging
from functools import singledispatch

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from chocolate_smart_home import models
from chocolate_smart_home.dependencies import db_session
import chocolate_smart_home.crud.device_types as device_types
import chocolate_smart_home.schemas as schemas
import chocolate_smart_home.utils as utils


logger = logging.getLogger()

@singledispatch
def create_device(db: Session, device_data: schemas.DeviceReceived) -> models.Device:
    logger.info("Creating device \"%s\"" % device_data)
    db_device = models.Device(
        mqtt_id=device_data.mqtt_id,
        device_type=device_types.get_new_or_existing_device_type_by_name(
            device_data.device_type_name
        ),
        remote_name=device_data.remote_name,
        name=device_data.name,
        online=True,
    )
    db.add(db_device)

    try:
        db.commit()
    except:
        db.rollback()
        raise

    db.refresh(db_device)
    return db_device


@create_device.register
def _(mqtt_id: str, device_type_name: str, remote_name: str, name: str) -> models.Device:
    device_data = schemas.DeviceReceived(
        mqtt_id=mqtt_id,
        device_type_name=device_type_name,
        remote_name=remote_name,
        name=name,
    )
    return create_device(db_session.get(), device_data)


@singledispatch
def update_device(db: Session, device_data: schemas.DeviceBase) -> models.Device:
    logger.info("Updating device \"%s\"" % device_data)
    db_device = get_device_by_mqtt_id(device_data.mqtt_id)
    db_device.device_type = (
        device_types.get_new_or_existing_device_type_by_name(device_data.device_type.name)
    )
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
    name: str
) -> models.Device:
    device_type = (
        device_types.get_new_or_existing_device_type_by_name(device_type_name)
    )
    device_type_schema = schemas.DeviceType(name=device_type_name, id=device_type.id)
    device_data = schemas.DeviceBase(
        mqtt_id=mqtt_id,
        device_type=device_type_schema,
        remote_name=remote_name,
        name=name
    )
    return update_device(db_session.get(), device_data)


def get_device_by_device_id(device_id: int) -> models.Device:
    return db_session.get().query(models.Device).filter(
        models.Device.id == device_id
    ).one()


def get_device_by_mqtt_id(mqtt_id: int) -> models.Device:
    return db_session.get().query(models.Device).filter(
        models.Device.mqtt_id == mqtt_id
    ).one()


def get_all_devices_data(db: Session) -> list[models.Device]:
    return db.query(models.Device).all()


def delete_device(*, Model, device_id: int) -> None:
    """Dynamically delete row of any device model."""
    model_name: str = utils.get_model_class_name(Model)
    logger.info("Deleting %s with id of \"%s\"" % (model_name, device_id))
    db: Session = db_session.get()

    try:
        device = db.query(Model).filter(Model.id == device_id).one()
    except NoResultFound:
        msg = (f"{model_name} deletion failed. No {model_name} "
               f"with an id of {device_id} found.")
        logger.error(msg)
        raise NoResultFound(msg)

    db.delete(device)
    db.flush()
    try:
        db.commit()
    except:
        db.rollback()
        raise
