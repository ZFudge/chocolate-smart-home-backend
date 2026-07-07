import logging
from typing import Type

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.database import Base
from src.dependencies import db_session
from src.utils import snakecase_to_pascalcase

logger = logging.getLogger()


def commit_db_object(device: Type[Base]) -> Type[Base]:
    db: Session = db_session.get()
    db.add(device)
    try:
        db.commit()
    except:
        db.rollback()
        raise

    db.refresh(device)
    return device


def get_device_type_names_with_model_exists() -> list[dict]:
    results = db_session.get().execute(
        text(
            """
        SELECT
            name AS device_type_name,
            EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = name
            ) AS has_plugin_model
        FROM
            device_types;"""
        )
    )
    return results.mappings().all()


def get_plugin_model_class_using_device_type_name(
    device_type_name: str,
) -> Type[Base] | None:
    plugin_model_class_name = snakecase_to_pascalcase(device_type_name)
    for mapper in Base.registry.mappers:
        if mapper.class_.__name__ == plugin_model_class_name:
            return mapper.class_


def get_plugin_db_obj_using_device_type_and_mqtt_id(
    device_type_name: str, mqtt_id: int
) -> Type[Base] | None:
    Table = get_plugin_model_class_using_device_type_name(device_type_name)
    return db_session.get().query(Table).where(Table.mqtt_id == mqtt_id).one_or_none()
