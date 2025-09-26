import logging

from sqlalchemy.exc import UniqueViolationError

from src.dependencies import db_session
from .model import Palette
from .palette_seeds import palette_presets

logger = logging.getLogger()


def seed_db():
    db = db_session.get()
    for name, colors in palette_presets:
        logger.info(f"Seeding palette: {name}")
        try:
            palette = Palette(name=name, colors=colors)
            db.add(palette)
        except UniqueViolationError:
            logger.error(f"Palette {name} already exists")
            continue
    db.commit()
