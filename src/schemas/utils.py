from typing import Any, Mapping, Type, Dict

import pydantic
from sqlalchemy.orm import collections
from sqlalchemy.orm.decl_api import DeclarativeMeta

from src import schemas, models


def to_schema(model_obj: Type[DeclarativeMeta] | None) -> Mapping | None:
    """Convert a sqlalchemy model object to its corresponding pydantic schema"""
    if model_obj is None:
        return None
    model_name: str = model_obj.__class__.__name__
    if model_name is None:
        return None
    pydantic_schema_cls: Type[pydantic.BaseModel] = getattr(schemas, model_name)
    schema_dict: Dict[str, Any] = dict()
    for name in pydantic_schema_cls.model_fields.keys():
        value: Any = getattr(model_obj, name)
        # Any attribute value that is also a sqlalchemy model object should be
        # recursively converted to its corresponding schema.
        if isinstance(type(value), DeclarativeMeta):
            value: Mapping = to_schema(value)
        elif isinstance(value, collections.InstrumentedList):
            value = map(to_schema, value)
        schema_dict[name] = value
    return pydantic_schema_cls(**schema_dict)


def device_mod_obj_to_frontend_schema(
    device: models.Device | None,
) -> schemas.DeviceFrontend | None:
    if device is None:
        return None
    return schemas.DeviceFrontend(
        mqtt_id=device.mqtt_id,
        remote_name=device.remote_name,
        name=device.name,
        device_type_name=device.device_type.name,
        tags=[tag.id for tag in device.tags] if device.tags else None,
        reboots=device.reboots,
        last_seen=str(device.last_seen) if device.last_seen else None,
        last_update_sent=(
            str(device.last_update_sent) if device.last_update_sent else None
        ),
    )
