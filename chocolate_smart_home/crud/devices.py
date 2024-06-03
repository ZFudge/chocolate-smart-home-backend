import logging

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from chocolate_smart_home import models
from chocolate_smart_home.dependencies import db_session
import chocolate_smart_home.utils as utils


logger = logging.getLogger()


def get_device_by_device_id(device_id: int) -> models.Device:
    return (
        db_session.get()
        .query(models.Device)
        .filter(models.Device.id == device_id)
        .one()
    )


def get_device_by_mqtt_client_id(mqtt_id: int) -> models.Device:
    db: Session = db_session.get()
    client = db.query(models.Client).filter(models.Client.mqtt_id == mqtt_id).one()
    return db.query(models.Device).filter(models.Device.client == client).one()


def get_all_devices_data(db: Session) -> list[models.Device]:
    return db.query(models.Device).all()


def delete_device(*, Model, device_id: int) -> None:
    """Dynamically delete row of any device model."""
    model_name: str = utils.get_model_class_name(Model)
    logger.info('Deleting %s with id of "%s"' % (model_name, device_id))
    db: Session = db_session.get()

    try:
        device = db.query(Model).filter(Model.id == device_id).one()
    except NoResultFound:
        msg = (
            f"{model_name} deletion failed. No {model_name} "
            f"with an id of {device_id} found."
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
