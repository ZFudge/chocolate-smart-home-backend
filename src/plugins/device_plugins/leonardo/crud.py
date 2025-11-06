import logging
from typing import List

from sqlalchemy.orm import Session

from src import dependencies, models
from src.mqtt import mqtt_client_ctx, topics
from .duplex_messenger import LeonardoDuplexMessenger


logger = logging.getLogger()
LEONARDO_SEND_TOPIC_TEMPLATE = topics.SEND_DEVICE_DATA_TEMPLATE.format(
    device_type="LEONARDO"
)


def get_all_leonardo_devices_data() -> List[models.Device]:
    db: Session = dependencies.db_session.get()
    leonardo_device_type = db.query(models.DeviceType).filter(models.DeviceType.name == "leonardo").one()
    return db.query(models.Device).filter(models.Device.device_type_id == leonardo_device_type.id).all()


def publish_message(*, leonardo_device_id: int, command: str):
    topic: str = LEONARDO_SEND_TOPIC_TEMPLATE.format(device_id=leonardo_device_id)
    outgoing_msg: str = LeonardoDuplexMessenger().compose_msg(command)
    mqtt_client_ctx.get().publish(topic=topic, message=outgoing_msg)
