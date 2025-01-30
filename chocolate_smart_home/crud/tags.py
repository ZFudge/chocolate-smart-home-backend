import logging
from typing import List

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

import chocolate_smart_home.schemas as schemas
from chocolate_smart_home import models
from chocolate_smart_home.dependencies import db_session


logger = logging.getLogger()


def get_tags() -> List[models.Tag]:
    db: Session = db_session.get()
    return db.query(models.Tag).all()


def get_tag_by_id(tag_id: int) -> models.Tag:
    return db_session.get().query(models.Tag).filter(models.Tag.id == tag_id).one()


def create_tag(new_tag: schemas.TagBase) -> models.Tag:
    logger.info('Creating tag "%s"' % new_tag)
    db: Session = db_session.get()

    new_tag = models.Tag(name=new_tag.name)
    db.add(new_tag)

    try:
        db.commit()
    except:
        db.rollback()
        raise

    db.refresh(new_tag)
    return new_tag


def get_new_or_existing_tag_by_name(tag_name: str) -> models.Tag:
    db: Session = db_session.get()
    tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
    if tag is None:
        return create_tag(tag_name)
    return tag


def update_tag(tag_id: int, tag_name: str) -> models.Tag:
    logger.info('Updating tag of id %s and name of "%s' % (tag_id, tag_name))
    db: Session = db_session.get()

    try:
        tag = db.query(models.Tag).filter(models.Tag.id == tag_id).one()
    except NoResultFound:
        msg = f"Tag update failed. No Tag object with an id of {tag_id} found."
        logger.error(msg)
        raise NoResultFound(msg)
    tag.name = tag_name

    db.add(tag)
    try:
        db.commit()
    except:
        db.rollback()
        raise

    db.refresh(tag)
    return tag


def delete_tag(tag_id: int) -> None:
    """Remove Tag object from any associated Devices, and delete the Tag object"""
    logger.info('Deleting tag of id "%s"' % tag_id)
    db: Session = db_session.get()

    try:
        tag = db.query(models.Tag).filter(models.Tag.id == tag_id).one()
    except NoResultFound as e:
        msg = "Failed to delete Tag with id of %s - %s" % (tag_id, e.args[0])
        logger.error(msg)
        raise NoResultFound(msg)
    devices_ids = [d.id for d in tag.devices]
    logger.info("%s %s" % (tag, f"{devices_ids=}"))

    for device in tag.devices:
        new_tags = [t for t in device.tags if t.id != tag_id]
        device.tags = new_tags
        db.add(device)

    db.delete(tag)

    try:
        db.commit()
    except:
        db.rollback()
        raise
