import logging
from typing import List

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from src import dependencies, models


logger = logging.getLogger()


def get_all_devices_data() -> List[models.Device]:
    db: Session = dependencies.db_session.get()
    return db.query(models.Device).all()


def get_device_by_device_id(device_id: int) -> models.Device:
    return (
        dependencies.db_session.get()
        .query(models.Device)
        .filter(models.Device.id == device_id)
        .one()
    )


def get_devices_by_mqtt_id(mqtt_id: int | List[int]) -> models.Device | List[models.Device]:
    logger.info(f"getting device by mqtt_id: {mqtt_id}")
    db: Session = dependencies.db_session.get()
    if isinstance(mqtt_id, list):
        return db.query(models.Device).filter(models.Device.mqtt_id.in_(mqtt_id)).all()
    return db.query(models.Device).filter(models.Device.mqtt_id == mqtt_id).one()


def delete_device(device_id: int) -> None:
    """Dynamically delete row of any device model."""
    logger.info('Deleting Device with id of "%s"' % device_id)
    db: Session = dependencies.db_session.get()

    try:
        device = db.query(models.Device).filter(models.Device.id == device_id).one()
    except NoResultFound:
        msg = "Device deletion failed. No Device with an id of %s found." % device_id
        logger.error(msg)
        raise NoResultFound(msg)

    db.delete(device)
    db.flush()
    try:
        db.commit()
    except:
        db.rollback()
        raise


def get_tags_by_ids(tag_ids: List[int|str]) -> List[models.Tag]:
    db: Session = dependencies.db_session.get()
    return db.query(models.Tag).filter(models.Tag.id.in_(tag_ids)).all()


def put_device_tags(device_mqtt_id: int, tag_ids: List[int|str]|None) -> models.Device:
    logger.info(f"Putting tags for device with mqtt id {device_mqtt_id} with tag ids {tag_ids}")
    if tag_ids is None:
        tag_ids = []
    logger.info(
        'Adding Tag(s) id(s) of %s to Device with mqtt id of "%s"' % (tag_ids, device_mqtt_id)
    )
    db: Session = dependencies.db_session.get()
    try:
        device = get_devices_by_mqtt_id(device_mqtt_id)
    except NoResultFound as e:
        msg = "Failed to add Tag id(s) of %s to " "Device of mqtt id %s - %s" % (
            tag_ids,
            device_mqtt_id,
            e.args[0],
        )
        logger.error(msg)
        raise NoResultFound(msg)

    device.tags = []

    if tag_ids:
        tags = get_tags_by_ids(tag_ids)
        if len(tags) == 0:
            msg = "Failed to add Tag id(s) of %s to " "Device of mqtt id %s - No Tag object(s) with id(s) %s found." % (
                tag_ids,
                device_mqtt_id,
                tag_ids,
            )
            logger.error(msg)
            raise NoResultFound(msg)
        for tag in tags:
            device.tags.append(tag)

    db.add(device)
    db.commit()
    db.refresh(device)

    return device


def add_device_tag(device_id: int, tag_id: int) -> models.Device:
    logger.info(
        'Adding Tag with id of %s to Device with id of "%s"' % (tag_id, device_id)
    )
    db: Session = dependencies.db_session.get()

    try:
        tag = db.query(models.Tag).filter(models.Tag.id == tag_id).one()
        device = get_device_by_device_id(device_id)
    except NoResultFound as e:
        msg = "Failed to add Tag of id %s to " "Device of id %s - %s" % (
            tag_id,
            device_id,
            e.args[0],
        )
        logger.error(msg)
        raise NoResultFound(msg)

    new_tags = device.tags
    if new_tags is None:
        new_tags = []
    if tag not in new_tags:
        new_tags.append(tag)
    device.tags = new_tags

    db.add(device)
    db.commit()
    db.refresh(device)

    return device


def remove_device_tag(device_id: int, tag_id: int) -> models.Device:
    logger.info(
        'Removing Tag with id of %s from Device with id of "%s"' % (tag_id, device_id)
    )
    db: Session = dependencies.db_session.get()

    try:
        device = get_device_by_device_id(device_id)
        tag = db.query(models.Tag).filter(models.Tag.id == tag_id).one()
    except NoResultFound as e:
        msg = "Failed to remove Tag from " "Device with id of %s - %s" % (
            device_id,
            e.args[0],
        )
        logger.error(msg)
        raise NoResultFound(msg)

    new_tags = device.tags
    if new_tags is None:
        new_tags = []
    else:
        new_tags.remove(tag)
    device.tags = new_tags
    db.add(device)
    db.commit()
    db.refresh(device)

    return device


def update_device_name(device_id: int, device_name: str) -> models.Device:
    logger.info(f"Updating device name for device with id {device_id} to {device_name}")
    db: Session = dependencies.db_session.get()
    try:
        device = get_device_by_device_id(device_id)
    except NoResultFound as e:
        msg = "Failed to update device name for " "Device with id of %s - %s" % (
            device_id,
            e.args[0],
        )
        logger.error(msg)
        raise NoResultFound(msg)
    device.name = device_name
    db.add(device)
    db.commit()
    db.refresh(device)
    return device
