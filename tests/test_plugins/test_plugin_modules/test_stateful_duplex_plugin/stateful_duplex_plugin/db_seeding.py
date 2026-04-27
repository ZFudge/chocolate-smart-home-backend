from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from . import models

PROPERTY_SEEDS = (
    ("property_1", "on"),
    ("property_2", "7"),
    ("property_3", "cabbage"),
)


def seed_db(db: Session):
    commit = False
    for pname, pvalue in PROPERTY_SEEDS:
        try:
            new_property = models.Properties(name=pname, value=pvalue)
            db.add(new_property)
            commit = True
        except SQLAlchemyError as e:
            print(e)
            continue
    if not commit:
        return
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
