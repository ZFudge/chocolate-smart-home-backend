import logging
from typing import Tuple, Type

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from src.crud.device_types import create_device_type, get_device_type_by_name
from src.crud.tags import get_tags_by_ids
from src.database import Base
from src.dependencies import db_session
from src.models import Device as DeviceModel, DeviceType as DeviceTypeModel
from src.schemas import DevicePatch, DeviceReceived
from src.utils import snakecase_to_pascalcase

logger = logging.getLogger()


def commit_db_object(device: Type[Base]) -> Type[Base]:
    db: Session = db_session.get()
    db.add(device)
    try:
        db.commit()
    except:
        db.rollback()
        raise

    db.refresh(device)
    return device


def get_devices() -> Tuple[DeviceModel]:
    return tuple(db_session.get().query(DeviceModel).all())


def get_device_by_id(mqtt_id: int) -> DeviceModel | None:
    return (
        db_session.get()
        .query(DeviceModel)
        .where(DeviceModel.mqtt_id == mqtt_id)
        .one_or_none()
    )


def delete_device(mqtt_id: int) -> None:
    """Dynamically delete row of any device model."""
    logger.info(f"Deleting Device with mqtt id of {mqtt_id}")
    db: Session = db_session.get()

    device = get_device_by_id(mqtt_id)
    if device is None:
        msg = (
            "Failed to delete device with mqtt id %s. No Device object with an mqtt id of %s found."
            % (mqtt_id, mqtt_id)
        )
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


def create_device(device: DeviceReceived) -> DeviceModel:
    logger.info('Creating Base device "%s"' % device.mqtt_id)
    device_type_name: str = device.device_type_name
    db_device_type: DeviceTypeModel = get_device_type_by_name(
        device_type_name
    ) or create_device_type(device_type_name)
    # TODO: lookup existing device name from previously exported settings
    truncated_remote_name = device.remote_name.split(" - ")[0]

    device_model = DeviceModel(
        mqtt_id=device.mqtt_id,
        remote_name=device.remote_name,
        name=truncated_remote_name,
        device_type=db_device_type,
    )
    new_device = commit_db_object(device_model)
    return new_device


def update_device(device: DeviceReceived, *_) -> DeviceModel:
    logger.info('Updating Base device "%s"' % device)
    db_device: DeviceModel = get_device_by_id(device.mqtt_id)
    if db_device is None:
        raise ValueError(f"Device with mqtt_id {device.mqtt_id} not found")

    if device.device_type_name != db_device.device_type.name:
        logger.warning(
            f"Device with mqtt_id {device.mqtt_id} has a different device type: {db_device.device_type.name} -> {device.device_type_name}"
        )
        device_type_db: DeviceTypeModel = get_device_type_by_name(
            device.device_type_name
        ) or create_device_type(device.device_type_name)
        db_device.device_type = device_type_db

    if db_device.remote_name != device.remote_name:
        db_device.reboots += 1
        db_device.remote_name = device.remote_name

    updated_device = commit_db_object(db_device)
    return updated_device


def get_plugin_model_class_using_device_type_name(
    device_type_name: str,
) -> DeviceModel | None:
    plugin_model_class_name = snakecase_to_pascalcase(device_type_name)
    for mapper in Base.registry.mappers:
        if mapper.class_.__name__ == plugin_model_class_name:
            return mapper.class_


def get_plugin_db_obj_using_device_type_and_mqtt_id(
    device_type_name: str, mqtt_id: int
) -> DeviceModel | None:
    Table = get_plugin_model_class_using_device_type_name(device_type_name)
    return db_session.get().query(Table).where(Table.mqtt_id == mqtt_id).one_or_none()
