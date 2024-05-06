import logging

from functools import singledispatch

from sqlalchemy.orm import Session

from chocolate_smart_home import models
from chocolate_smart_home.dependencies import db_session
import chocolate_smart_home.schemas as schemas


logger = logging.getLogger()

@singledispatch
def create_device_type(db: Session,
                       device_type_name: str) -> models.DeviceType:
    logger.info('Creating device_type "%s"' % device_type_name)
    db_device_type = models.DeviceType(name=device_type_name)
    db.add(db_device_type)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(db_device_type)
    return db_device_type


@create_device_type.register
def _(device_type_name: str) -> models.DeviceType:
    return create_device_type(db_session.get(), device_type_name)


def get_new_or_existing_device_type_by_name(device_type_name: schemas.DeviceTypeBase) -> models.DeviceType:
    db = db_session.get()
    device_type = db.query(models.DeviceType).filter(
        models.DeviceType.name == device_type_name
    ).first()
    if device_type is None:
        return create_device_type(db, device_type_name)
    return device_type
