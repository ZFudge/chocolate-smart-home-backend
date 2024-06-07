import logging
from typing import List

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

import chocolate_smart_home.schemas as schemas
from chocolate_smart_home import models
from chocolate_smart_home.dependencies import db_session


logger = logging.getLogger()


def get_spaces() -> List[models.Space]:
    db: Session = db_session.get()
    return db.query(models.Space).all()


def get_space_by_id(space_id: int) -> models.Space:
    return (
        db_session.get()
        .query(models.Space)
        .filter(models.Space.id == space_id)
        .one()
    )


def create_space(new_space: schemas.SpaceBase) -> models.Space:
    logger.info('Creating space "%s"' % new_space)
    db: Session = db_session.get()

    new_space = models.Space(name=new_space.name)
    db.add(new_space)

    try:
        db.commit()
    except:
        db.rollback()
        raise

    db.refresh(new_space)
    return new_space


def get_new_or_existing_space_by_name(space_name: str) -> models.Space:
    db: Session = db_session.get()
    space = db.query(models.Space).filter(models.Space.name == space_name).first()
    if space is None:
        return create_space(space_name)
    return space


def update_space(space_id: int, space_name: str) -> models.Space:
    logger.info('Updating space of id %s and name of "%s' % (space_id, space_name))
    db: Session = db_session.get()

    try:
        space = db.query(models.Space).filter(models.Space.id == space_id).one()
    except NoResultFound:
        msg = (
            f"Space update failed. No Space object "
            f"with an id of {space_id} found."
        )
        logger.error(msg)
        raise NoResultFound(msg)
    space.name = space_name

    db.add(space)
    try:
        db.commit()
    except:
        db.rollback()
        raise

    db.refresh(space)
    return space


def delete_space(space_id: int) -> None:
    """Remove Space object from any associated Devices, and delete the Space object"""
    logger.info('Deleting space of id "%s"' % space_id)
    db: Session = db_session.get()

    try:
        space = db.query(models.Space).filter(models.Space.id == space_id).one()
    except NoResultFound as e:
        msg = "Failed to delete Space with id of %s - %s" % (space_id, e.args[0])
        logger.error(msg)
        raise NoResultFound(msg)
    devices_ids = [d.id for d in space.devices]
    logger.info(space, f"{devices_ids=}")

    for device in space.devices:
        device.space = None
        db.add(device)

    db.delete(space)

    try:
        db.commit()
    except:
        db.rollback()
        raise
