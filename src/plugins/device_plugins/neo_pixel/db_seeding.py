import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from . import models, palette_presets as presets, utils

logger = logging.getLogger(__name__)


def seed_db(db: Session):
    commit = False
    for name, colors_27_byte in presets.palette_presets:
        colors = utils.convert_27_byte_int_to_9_hex_str(colors_27_byte)
        try:
            new_palette = models.Palette(name=name, colors=colors)
            db.add(new_palette)
            commit = True
        except SQLAlchemyError as e:
            logger.error(e)
            continue
    if not commit:
        return
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
