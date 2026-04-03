import datetime as dt
import logging
from typing import Tuple

from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.orm import Session

from src.crud.tags import get_tags_by_ids
from src.schemas import DevicePatch
from src.models import Device as DeviceModel
from src.dependencies import db_session


logger = logging.getLogger()


def get_devices() -> Tuple[DeviceModel]:
    return tuple(db_session.get().query(DeviceModel).all())

def get_device_by_id(mqtt_id: int) -> DeviceModel | None:
    return (
        db_session.get()
        .query(DeviceModel)
        .filter(DeviceModel.mqtt_id == mqtt_id)
        .one_or_none()
    )

def delete_device(mqtt_id: int) -> None:
    """Dynamically delete row of any device model."""
    logger.info(f'Deleting Device with mqtt id of {mqtt_id}')
    db: Session = db_session.get()

    device = get_device_by_id(mqtt_id)
    if device is None:
        msg = "Failed to delete device with mqtt id %s. No Device object with an mqtt id of %s found." % (mqtt_id, mqtt_id)
        logger.error(msg)
        raise NoResultFound(msg)

    db.delete(device)
    db.flush()
    try:
        db.commit()
    except:
        db.rollback()
        raise

def patch_device(patch_device: DevicePatch) -> DeviceModel:
    device = get_device_by_id(patch_device.mqtt_id)
    if device is None:
        msg = (
            f"Failed to patch device with mqtt id {patch_device.mqtt_id}. "
            f"No Device object with an mqtt id of {patch_device.mqtt_id} found."
        )
        logger.error(msg)
        raise NoResultFound(msg)

    if patch_device.tags is not None:
        tags = get_tags_by_ids(patch_device.tags)
        device.tags = list(filter(None, tags))
    if patch_device.name is not None:
        device.name = patch_device.name

    db: Session = db_session.get()
    db.add(device)
    try:
        db.commit()
    except:
        db.rollback()
        raise
    db.refresh(device)
    return device

def update_last_update_sent_if_exists(mqtt_id: int):
    db: Session = db_session.get()
    try:
        device = get_device_by_id(mqtt_id)
        if device is None:
            raise NoResultFound(f"Device with mqtt id {mqtt_id} not found")
        device.last_update_sent = dt.datetime.now()
        db.add(device)
        db.commit()
    except (SQLAlchemyError, NoResultFound) as e:
        (detail,) = e.args
        db.rollback()
        logger.error("Failed to update last update sent for Device with an id of %s: %s" % (mqtt_id, detail))
