import logging
from datetime import datetime as dt
from typing import Dict, List, Tuple, Type

from sqlalchemy import text
from sqlalchemy.engine.result import MappingResult
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from src import crud, models, schemas, utils
from src.database import Base
from src.dependencies import db_session

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


def get_device_type_names_with_model_exists() -> List[Dict]:
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


def get_devices() -> Tuple[MappingResult]:
    models_exist_by_device_type = get_device_type_names_with_model_exists()
    PLUGIN_CASE_WHENS = ""
    PLUGIN_TABLE_LEFT_JOINS = ""
    PLUGIN_GROUP_BYS = ""
    for device_type_dict in models_exist_by_device_type:
        plugin_name = device_type_dict["device_type_name"]
        abbreviation = "".join([w[0] for w in plugin_name.split("_")])
        if not device_type_dict["has_plugin_model"]:
            continue
        PLUGIN_CASE_WHENS += f"""
                WHEN dt.name = '{plugin_name}' THEN row_to_json({abbreviation})"""
        PLUGIN_TABLE_LEFT_JOINS += f"""
        LEFT JOIN
            {plugin_name} {abbreviation} ON d.mqtt_id = {abbreviation}.mqtt_id AND dt.name = '{plugin_name}'"""
        PLUGIN_GROUP_BYS += f""",
            {abbreviation}.*"""
    PLUGIN_CASES = ""
    if PLUGIN_CASE_WHENS:
        PLUGIN_CASES = f""",
            CASE{PLUGIN_CASE_WHENS}
                ELSE null
            END AS plugin"""
    raw_sql = f"""
        SELECT
            d.mqtt_id,
            d.name,
            d.remote_name,
            d.reboots,
            d.last_seen,
            d.last_update_sent,
            dt.name AS device_type_name,
            dtags.tag_ids{PLUGIN_CASES}
        FROM
            devices d
        LEFT JOIN
            device_types dt ON d.device_type_id = dt.id
        LEFT JOIN
            (
                SELECT
                    mqtt_id,
                    JSON_AGG(tag_id)::TEXT AS tag_ids
                FROM
                    device_tags
                GROUP BY
                    mqtt_id
            ) dtags ON d.mqtt_id = dtags.mqtt_id{PLUGIN_TABLE_LEFT_JOINS}
        GROUP BY
            d.mqtt_id,
            dt.name,
            dtags.tag_ids{PLUGIN_GROUP_BYS}
        ORDER BY
            dt.name,
            d.mqtt_id;"""
    logger.info(raw_sql)
    results = db_session.get().execute(text(raw_sql))
    return tuple(results.mappings().all())


def get_device_by_id(mqtt_id: int) -> models.Device | None:
    return (
        db_session.get()
        .query(models.Device)
        .where(models.Device.mqtt_id == mqtt_id)
        .one_or_none()
    )


def delete_device(mqtt_id: int) -> None:
    """Dynamically delete row of any device model."""
    logger.info(f"Deleting Device with mqtt id of {mqtt_id}")
    db: Session = db_session.get()

    device = get_device_by_id(mqtt_id)
    if device is None:
        msg = (
            "Failed to delete device with mqtt id %s. No Device object with an mqtt id of %s found."
            % (mqtt_id, mqtt_id)
        )
        logger.error(msg)
        raise NoResultFound(msg)

    db.delete(device)
    db.flush()
    try:
        db.commit()
    except:
        db.rollback()
        raise


def patch_device(patch_device: schemas.DevicePatch) -> models.Device:
    device = get_device_by_id(patch_device.mqtt_id)
    if device is None:
        msg = (
            f"Failed to patch device with mqtt id {patch_device.mqtt_id}. "
            f"No Device object with an mqtt id of {patch_device.mqtt_id} found."
        )
        logger.error(msg)
        raise NoResultFound(msg)

    if patch_device.tags is not None:
        tags = crud.get_tags_by_ids(patch_device.tags)
        device.tags = list(filter(None, tags))
    if patch_device.name is not None:
        device.name = patch_device.name

    db: Session = db_session.get()
    db.add(device)
    try:
        db.commit()
    except:
        db.rollback()
        raise
    db.refresh(device)
    return device


def create_device(device: schemas.DeviceReceived) -> models.Device:
    logger.info('Creating Base device "%s"' % device.mqtt_id)
    device_type_name: str = device.device_type_name
    db_device_type: models.DeviceType = crud.get_device_type_by_name(
        device_type_name
    ) or crud.create_device_type(device_type_name)
    # TODO: lookup existing device name from previously exported settings
    truncated_remote_name = device.remote_name.split(" - ")[0]

    device_model = models.Device(
        mqtt_id=device.mqtt_id,
        remote_name=device.remote_name,
        name=truncated_remote_name,
        device_type=db_device_type,
    )
    new_device = commit_db_object(device_model)
    return new_device


def update_device(device: schemas.DeviceReceived, *_) -> models.Device:
    logger.info('Updating Base device "%s"' % device)
    db_device: models.Device = get_device_by_id(device.mqtt_id)
    if db_device is None:
        raise ValueError(f"Device with mqtt_id {device.mqtt_id} not found")

    if device.device_type_name != db_device.device_type.name:
        logger.warning(
            f"Device with mqtt_id {device.mqtt_id} has a different device type: {db_device.device_type.name} -> {device.device_type_name}"
        )
        device_type_db: models.DeviceType = crud.get_device_type_by_name(
            device.device_type_name
        ) or crud.create_device_type(device.device_type_name)
        db_device.device_type = device_type_db

    if db_device.remote_name != device.remote_name:
        db_device.reboots += 1
        db_device.remote_name = device.remote_name

    updated_device = commit_db_object(db_device)
    return updated_device


def get_plugin_model_class_using_device_type_name(
    device_type_name: str,
) -> models.Device | None:
    plugin_model_class_name = utils.snakecase_to_pascalcase(device_type_name)
    for mapper in Base.registry.mappers:
        if mapper.class_.__name__ == plugin_model_class_name:
            return mapper.class_


def get_plugin_db_obj_using_device_type_and_mqtt_id(
    device_type_name: str, mqtt_id: int
) -> models.Device | None:
    Table = get_plugin_model_class_using_device_type_name(device_type_name)
    return db_session.get().query(Table).where(Table.mqtt_id == mqtt_id).one_or_none()


def set_last_update_sent_to_current_time(mqtt_id: int):
    db_device: models.Device = get_device_by_id(mqtt_id)
    if db_device is None:
        raise ValueError(f"Device with mqtt_id {mqtt_id} not found")

    db_device.last_update_sent = dt.now()

    updated_device = commit_db_object(db_device)
    return updated_device


def set_last_seen_to_current_time(mqtt_id: int):
    db_device: models.Device = get_device_by_id(mqtt_id)
    if db_device is None:
        return

    db_device.last_seen = dt.now()

    updated_device = commit_db_object(db_device)
    return updated_device
