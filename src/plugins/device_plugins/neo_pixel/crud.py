import logging
from typing import List

from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.orm import Session

from src import dependencies
from src.mqtt import mqtt_client_ctx, topics
from .duplex_messenger import NeoPixelDuplexMessenger
from .model import NeoPixel, Palette
from .schemas import CreateBytesPaletteSchema, CreateHexPaletteSchema
from .utils import hex_list_to_byte_tuple

logger = logging.getLogger()
NEO_PIXEL_SEND_TOPIC_TEMPLATE = topics.SEND_DEVICE_DATA_TEMPLATE.format(
    device_type="neo_pixel"
)


def get_all_neo_pixel_devices_data() -> List[NeoPixel]:
    db: Session = dependencies.db_session.get()
    return db.query(NeoPixel).all()


def get_neo_pixel_device_by_device_id(neo_pixel_device_id: int) -> NeoPixel:
    logger.info('Retrieving NeoPixel with id of "%s"' % neo_pixel_device_id)
    db: Session = dependencies.db_session.get()

    try:
        neo_pixel_device = (
            db.query(NeoPixel).filter(NeoPixel.id == neo_pixel_device_id).one()
        )
    except NoResultFound:
        raise NoResultFound(f"No NeoPixel with an id of {neo_pixel_device_id} found.")

    return neo_pixel_device


def publish_message(*, neo_pixel_device_id: int, data: dict):
    topic: str = NEO_PIXEL_SEND_TOPIC_TEMPLATE.format(device_id=neo_pixel_device_id)
    outgoing_msg: str = NeoPixelDuplexMessenger().compose_msg(data)
    mqtt_client_ctx.get().publish(topic=topic, message=outgoing_msg)


def delete_neo_pixel_device(neo_pixel_device_id: int):
    """Delete row from neo_pixel_devices table, then delete its corresponding row from devices table."""
    logger.info('Deleting NeoPixel with id of "%s"' % neo_pixel_device_id)
    db: Session = dependencies.db_session.get()

    try:
        neo_pixel_device = (
            db.query(NeoPixel).filter(NeoPixel.id == neo_pixel_device_id).one()
        )
    except NoResultFound:
        raise NoResultFound(f"No NeoPixel with an id of {neo_pixel_device_id} found.")

    device = neo_pixel_device.device

    db.delete(neo_pixel_device)
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


def get_all_palettes() -> List[Palette]:
    db: Session = dependencies.db_session.get()
    return db.query(Palette).all()


def create_palette(palette: CreateBytesPaletteSchema):
    db: Session = dependencies.db_session.get()
    try:
        db_palette = Palette(name=palette.name, colors=palette.colors)
        db.add(db_palette)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise SQLAlchemyError("Palette with name %s already exists" % palette.name)
    db.refresh(db_palette)
    return db_palette


def create_palette_from_hex_strs(palette: CreateHexPaletteSchema):
    return create_palette(
        CreateBytesPaletteSchema(
            name=palette.name,
            colors=hex_list_to_byte_tuple(palette.colors)
        )
    )
