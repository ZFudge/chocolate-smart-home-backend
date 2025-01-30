import logging
from typing import List

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from src import dependencies
from src.mqtt import mqtt_client_ctx, topics
from .duplex_messenger import OnOffDuplexMessenger
from .model import OnOff


logger = logging.getLogger()
ON_OFF_SEND_TOPIC_TEMPLATE = topics.SEND_DEVICE_DATA_TEMPLATE.format(
    device_type="on_off"
)


def get_all_on_off_devices_data() -> List[OnOff]:
    db: Session = dependencies.db_session.get()
    return db.query(OnOff).all()


def get_on_off_device_by_device_id(on_off_device_id: int) -> OnOff:
    logger.info('Retrieving OnOff with id of "%s"' % on_off_device_id)
    db: Session = dependencies.db_session.get()

    try:
        on_off_device = db.query(OnOff).filter(OnOff.id == on_off_device_id).one()
    except NoResultFound:
        raise NoResultFound(f"No OnOff with an id of {on_off_device_id} found.")

    return on_off_device


def publish_message(*, on_off_device_id: int, on: bool):
    topic: str = ON_OFF_SEND_TOPIC_TEMPLATE.format(device_id=on_off_device_id)
    outgoing_msg: str = OnOffDuplexMessenger().compose_msg(on)
    mqtt_client_ctx.get().publish(topic=topic, message=outgoing_msg)


def delete_on_off_device(on_off_device_id: int):
    """Delete row from on_off_devices table, then delete its corresponding row from devices table."""
    logger.info('Deleting OnOff with id of "%s"' % on_off_device_id)
    db: Session = dependencies.db_session.get()

    try:
        on_off_device = db.query(OnOff).filter(OnOff.id == on_off_device_id).one()
    except NoResultFound:
        raise NoResultFound(f"No OnOff with an id of {on_off_device_id} found.")

    device = on_off_device.device

    db.delete(on_off_device)
    db.flush()
    try:
        db.commit()
    except:
        db.rollback()
        raise

    logger.info('Deleting Device with id of "%s"' % device.id)

    db.delete(device)
    db.flush()
    try:
        db.commit()
    except:
        db.rollback()
        raise
