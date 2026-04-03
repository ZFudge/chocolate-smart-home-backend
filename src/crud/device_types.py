import logging

from functools import singledispatch

from src.models import DeviceType as DeviceTypeModel
from src.dependencies import db_session


logger = logging.getLogger()


@singledispatch
def create_device_type(device_type_name: str) -> DeviceTypeModel:
    logger.info('Creating device_type "%s"' % device_type_name)

    device_type = DeviceTypeModel(name=device_type_name)
    db = db_session.get()
    db.add(device_type)

    try:
        db.commit()
    except:
        db.rollback()
        raise

    db.refresh(device_type)
    return device_type

def get_device_type_by_name(device_type_name: str) -> DeviceTypeModel:
    return db_session.get().query(DeviceTypeModel).filter(DeviceTypeModel.name == device_type_name).one_or_none()

