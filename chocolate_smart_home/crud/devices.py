import logging
from typing import List

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from chocolate_smart_home import dependencies, models


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


def get_device_by_mqtt_client_id(mqtt_id: int) -> models.Device:
    db: Session = dependencies.db_session.get()
    return db.query(models.Client).filter(models.Client.mqtt_id == mqtt_id).one().device


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


def add_device_space(device_id: int, space_id: int) -> models.Device:
    logger.info('Adding Space with id of %s to Device with id of "%s"' % (space_id, device_id))
    db: Session = dependencies.db_session.get()

    try:
        space = db.query(models.Space).filter(models.Space.id == space_id).one()
        device = db.query(models.Device).filter(models.Device.id == device_id).one()
    except NoResultFound as e:
        msg = (
            "Failed to add Space with id of %s to "
            "Device with id of %s - %s" % (space_id, device_id, e.args[0])
        )
        logger.error(msg)
        raise NoResultFound(msg)

    device.space = space
    db.add(device)
    db.commit()
    db.refresh(device)

    return device


def remove_device_space(device_id: int) -> models.Device:
    logger.info('Adding Space with id of %s to Device with id of "%s"' % (device_id, device_id))
    db: Session = dependencies.db_session.get()

    try:
        device = db.query(models.Device).filter(models.Device.id == device_id).one()
    except NoResultFound as e:
        msg = (
            "Failed to remove Space from "
            "Device with id of %s - %s" % (device_id, e.args[0])
        )
        logger.error(msg)
        raise NoResultFound(msg)

    device.space = None
    db.add(device)
    db.commit()
    db.refresh(device)

    return device
