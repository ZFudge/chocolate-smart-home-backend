from typing import Any, List, Mapping, Tuple, Type

import pydantic
from sqlalchemy.orm.decl_api import DeclarativeMeta

from chocolate_smart_home import models, schemas


def to_schema(model_obj: Type[DeclarativeMeta]) -> Mapping:
    """Return a sqlalchemy model object's data in its corresponding pydantic schema"""
    if model_obj is None:
        return None
    model_name: str = models.get_model_class_name(model_obj)
    schema_cls: Type[pydantic.BaseModel] = getattr(schemas, model_name)
    attr_name_value_pairs: List[Tuple[str, Any]] = []

    for name in schema_cls.model_fields.keys():
        value: Any = getattr(model_obj, name)
        # Any attribute value that is also a sqlalchemy model object should be
        # recursively converted to its corresponding schema.
        if type(type(value)) is DeclarativeMeta:
            value: Mapping = to_schema(value)
        attr_name_value_pairs.append((name, value))

    return schema_cls(**dict(attr_name_value_pairs))
