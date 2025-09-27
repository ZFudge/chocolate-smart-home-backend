"""
Automatically seeds the database with plugin model data.
Will be automatically discovered and executed from discovered_plugins.py on application startup.
"""
import logging

from sqlalchemy.exc import SQLAlchemyError

from src.dependencies import db_session
from .model import Palette
from .palette_seeds import palette_presets

logger = logging.getLogger()

logger.info("Neo Pixel db_seeding module imported")

def seed_db():
    logger.info("Seeding Neo Pixel models...")
    db = db_session.get()
    commit = False

    for name, colors in palette_presets:
        logger.info(f"Seeding palette: {name}")
        try:
            palette = Palette(name=name, colors=colors)
            db.add(palette)
            commit = True
        except SQLAlchemyError:
            logger.error(f"Palette {name} already exists")
            continue

    if commit:
        try:
            db.commit()
            logger.info("Neo Pixel models seeded successfully")
        except SQLAlchemyError:
            db.rollback()
            logger.error("Error committing Neo Pixel models")
