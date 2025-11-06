from typing import Any, Mapping, Type, Dict

import pydantic
from sqlalchemy.orm import collections
from sqlalchemy.orm.decl_api import DeclarativeMeta

from src import schemas


def to_schema(model_obj: Type[DeclarativeMeta]|None) -> Mapping|None:
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
