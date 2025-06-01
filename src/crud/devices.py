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


def get_device_by_mqtt_id(mqtt_id: int | List[int]) -> models.Device:
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


def add_device_tag(device_id: int, tag_id: int) -> models.Device:
    logger.info(
        'Adding Tag with id of %s to Device with id of "%s"' % (tag_id, device_id)
    )
    db: Session = dependencies.db_session.get()

    try:
        tag = db.query(models.Tag).filter(models.Tag.id == tag_id).one()
        device = db.query(models.Device).filter(models.Device.id == device_id).one()
    except NoResultFound as e:
        msg = "Failed to add Tag with id of %s to " "Device with id of %s - %s" % (
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
        device = db.query(models.Device).filter(models.Device.id == device_id).one()
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
