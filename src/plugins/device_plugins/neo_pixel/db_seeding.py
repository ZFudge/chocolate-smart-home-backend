import csv
import logging

from sqlalchemy.orm import Session

from . import models, utils

logger = logging.getLogger(__name__)


def seed_db(db: Session) -> bool:
    commit = False
    location = __file__.rpartition("/")[0]
    with open(
        location + "/palette_presets.csv", mode="r", newline="", encoding="utf-8"
    ) as file:
        reader = csv.reader(file)
        for row in reader:
            name = row[0]
            color_bytes = list(map(int, row[1:]))
            colors = utils.convert_27_byte_int_to_9_hex_str(color_bytes)
            new_palette = models.Palette(name=name, colors=colors)
            db.add(new_palette)
            commit = True
    return commit
