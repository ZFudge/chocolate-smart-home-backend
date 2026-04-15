import logging
from typing import Tuple

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

import src.schemas as schemas
from src.models import Tag as TagModel
from src.dependencies import db_session


logger = logging.getLogger()


def get_tags() -> Tuple[TagModel]:
    return tuple(db_session.get().query(TagModel).all())


def get_tag_by_id(tag_id: int) -> TagModel | None:
    return db_session.get().query(TagModel).where(TagModel.id == tag_id).one_or_none()


def get_tags_by_ids(tag_ids: Tuple[int, ...]) -> Tuple[TagModel, ...]:
    return tuple(map(get_tag_by_id, tag_ids))


def get_tag_by_name(tag_name: str) -> TagModel | None:
    return (
        db_session.get().query(TagModel).where(TagModel.name == tag_name).one_or_none()
    )


def create_tag(tag_name: str) -> TagModel:
    db: Session = db_session.get()

    new_tag = TagModel(name=tag_name)
    db.add(new_tag)

    try:
        db.commit()
    except:
        db.rollback()
        raise

    db.refresh(new_tag)
    return new_tag


def patch_tag(patch_tag: schemas.TagPatch) -> TagModel:
    logger.info(
        'Updating tag of id %s and name of "%s' % (patch_tag.id, patch_tag.name)
    )
    db: Session = db_session.get()

    tag_obj = get_tag_by_id(patch_tag.id)
    if tag_obj is None:
        msg = f"Tag update failed. No Tag object with an id of {patch_tag.id} found."
        logger.error(msg)
        raise NoResultFound(msg)

    tag_obj.name = patch_tag.name
    db.add(tag_obj)
    try:
        db.commit()
    except:
        db.rollback()
        raise

    db.refresh(tag_obj)
    return tag_obj


def delete_tag(tag_id: int) -> None:
    """Remove Tag object from any associated Devices, and delete the Tag object"""
    logger.info('Deleting tag of id "%s"' % tag_id)
    db: Session = db_session.get()

    tag: TagModel | None = get_tag_by_id(tag_id)
    if tag is None:
        msg = f"Failed to delete Tag with id of {tag_id}. No Tag object with an id of {tag_id} found."
        logger.error(msg)
        raise NoResultFound(msg)
    devices_ids = [d.mqtt_id for d in tag.devices]
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
