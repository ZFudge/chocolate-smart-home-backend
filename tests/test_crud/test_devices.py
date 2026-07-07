from datetime import datetime as dt
from unittest.mock import patch

import pytest
from sqlalchemy.exc import NoResultFound

from src import crud, models, schemas


def test_crud_get_device_by_id_returns_device(populated_test_db):
    device = crud.get_device_by_id(234)
    assert isinstance(device, models.Device)
    assert device.mqtt_id == 234
    assert device.device_type.name == "TEST_DEVICE_TYPE_NAME_2"
    assert device.remote_name == "Remote Name 2 - 2"
    assert device.name == "Test Device Name 2"


def test_crud_get_device_by_id_returns_none_when_device_does_not_exist(empty_test_db):
    assert crud.get_device_by_id(123) is None


def test_crud_get_devices_returns_empty(empty_test_db):
    assert crud.get_devices() == ()


def test_crud_get_devices_query_basic(empty_test_db):
    expected_sql = """
        SELECT
            d.mqtt_id,
            d.name,
            d.remote_name,
            d.reboots,
            d.last_seen,
            d.last_update_sent,
            dt.name AS device_type_name,
            dtags.tag_ids
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
            ) dtags ON d.mqtt_id = dtags.mqtt_id
        GROUP BY
            d.mqtt_id,
            dt.name,
            dtags.tag_ids
        ORDER BY
            dt.name,
            d.mqtt_id;"""
    with (
        patch("src.crud.devices.db_session") as db_session,
        patch("src.crud.utils.db_session") as utils_db_session,
        patch("src.crud.devices.logger.info") as mock_logger,
    ):
        crud.get_devices()
        assert db_session.get().execute.call_count == 1
        assert utils_db_session.get().execute.call_count == 1
        mock_logger.assert_called_once_with(expected_sql)


def test_crud_get_devices_query_with_cases(populated_test_db):
    expected_sql = """
        SELECT
            d.mqtt_id,
            d.name,
            d.remote_name,
            d.reboots,
            d.last_seen,
            d.last_update_sent,
            dt.name AS device_type_name,
            dtags.tag_ids,
            CASE
                WHEN dt.name = 'example_plugin' THEN row_to_json(ep)
                ELSE null
            END AS plugin
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
            ) dtags ON d.mqtt_id = dtags.mqtt_id
        LEFT JOIN
            example_plugin ep ON d.mqtt_id = ep.mqtt_id AND dt.name = 'example_plugin'
        GROUP BY
            d.mqtt_id,
            dt.name,
            dtags.tag_ids,
            ep.*
        ORDER BY
            dt.name,
            d.mqtt_id;"""
    with (
        patch("src.crud.devices.db_session") as db_session,
        patch(
            "src.crud.devices.get_device_type_names_with_model_exists",
            return_value=[
                {
                    "device_type_name": "example_plugin",
                    "has_plugin_model": True,
                },
                {
                    "device_type_name": "example_no_model_plugin",
                    "has_plugin_model": False,
                },
            ],
        ),
        patch("src.crud.devices.logger.info") as mock_logger,
    ):
        crud.get_devices()
        mock_logger.assert_called_once_with(expected_sql)
        db_session.get().execute.assert_called_once()


def test_crud_get_devices_returns_devices(populated_test_db):
    devices = crud.get_devices()
    assert len(devices) == 3
    device_1, device_2, device_3 = devices
    assert device_1.mqtt_id == 123
    assert device_1.device_type_name == "TEST_DEVICE_TYPE_NAME_1"
    assert device_1.remote_name == "Remote Name 1 - 1"
    assert device_1.name == "Test Device Name 1"
    assert device_2.mqtt_id == 234
    assert device_2.device_type_name == "TEST_DEVICE_TYPE_NAME_2"
    assert device_2.remote_name == "Remote Name 2 - 2"
    assert device_2.name == "Test Device Name 2"
    assert device_3.mqtt_id == 345
    assert device_3.device_type_name == "TEST_DEVICE_TYPE_NAME_2"
    assert device_3.remote_name == "Remote Name 3 - 3"
    assert device_3.name == "Test Device Name 3"


def test_crud_delete_device_deletes_device(populated_test_db):
    crud.delete_device(mqtt_id=123)
    assert len(crud.get_devices()) == 2
    crud.delete_device(mqtt_id=234)
    assert len(crud.get_devices()) == 1


def test_crud_delete_device_with_schedule_job(populated_test_db):
    crud.delete_device(mqtt_id=345)
    assert crud.get_device_by_id(345) is None


def test_crud_delete_device_fails_when_device_does_not_exist(empty_test_db):
    with pytest.raises(NoResultFound):
        crud.delete_device(mqtt_id=123)


def test_crud_create_device_creates_device(empty_test_db):
    crud.create_device(
        schemas.DeviceReceived(
            device_type_name="test_device_type_name",
            mqtt_id=123,
            remote_name="test_remote_name - 123",
        )
    )
    device = (
        empty_test_db.query(models.Device).where(models.Device.mqtt_id == 123).first()
    )
    assert device.mqtt_id == 123
    assert device.device_type.name == "test_device_type_name"
    assert device.remote_name == "test_remote_name - 123"
    assert device.name == "test_remote_name"


def test_crud_create_device_does_not_set_last_seen_or_last_update_sent_values(
    empty_test_db,
):
    crud.create_device(
        schemas.DeviceReceived(
            device_type_name="test_device_type_name",
            mqtt_id=123,
            remote_name="test_remote_name - 123",
        )
    )
    device = (
        empty_test_db.query(models.Device).where(models.Device.mqtt_id == 123).first()
    )
    assert device.last_seen is None
    assert device.last_update_sent is None


def test_crud_create_device_sets_reboots_with_zero_value(empty_test_db):
    crud.create_device(
        schemas.DeviceReceived(
            device_type_name="test_device_type_name",
            mqtt_id=123,
            remote_name="test_remote_name - 123",
        )
    )
    device = (
        empty_test_db.query(models.Device).where(models.Device.mqtt_id == 123).first()
    )
    assert device.reboots == 0


def test_crud_create_device_sets_created_date(empty_test_db):
    d = dt.now()
    crud.create_device(
        schemas.DeviceReceived(
            device_type_name="test_device_type_name",
            mqtt_id=123,
            remote_name="test_remote_name - 123",
        )
    )
    device = (
        empty_test_db.query(models.Device).where(models.Device.mqtt_id == 123).first()
    )
    assert device.created_date > d


def test_crud_update_device_raises_ValueError(empty_test_db):
    with pytest.raises(ValueError):
        crud.update_device(
            schemas.DeviceReceived(
                device_type_name="TEST_DEVICE_TYPE_NAME_1",
                mqtt_id=123,
                remote_name="new_test_remote_name",
            )
        )


def test_crud_update_device_sets_remote_name(populated_test_db):
    crud.update_device(
        schemas.DeviceReceived(
            device_type_name="TEST_DEVICE_TYPE_NAME_1",
            mqtt_id=123,
            remote_name="new_test_remote_name",
        )
    )
    device = (
        populated_test_db.query(models.Device)
        .where(models.Device.mqtt_id == 123)
        .first()
    )
    assert device.remote_name == "new_test_remote_name"


def test_crud_update_device_increments_reboots_when_remote_name_changed(
    populated_test_db,
):
    crud.update_device(
        schemas.DeviceReceived(
            device_type_name="TEST_DEVICE_TYPE_NAME_1",
            mqtt_id=123,
            remote_name="test_remote_name",
        )
    )
    device = (
        populated_test_db.query(models.Device)
        .where(models.Device.mqtt_id == 123)
        .first()
    )
    assert device.reboots == 1


def test_crud_update_device_does_not_increment_reboots_when_remote_name_not_changed(
    populated_test_db,
):
    crud.update_device(
        schemas.DeviceReceived(
            device_type_name="TEST_DEVICE_TYPE_NAME_1",
            mqtt_id=123,
            remote_name="Remote Name 1 - 1",
        )
    )
    device = (
        populated_test_db.query(models.Device)
        .where(models.Device.mqtt_id == 123)
        .first()
    )
    assert device.reboots == 0


def test_crud_update_device_can_change_device_type(populated_test_db):
    crud.update_device(
        schemas.DeviceReceived(
            device_type_name="new_test_device_type_name",
            mqtt_id=123,
            remote_name="Remote Name 1 - 1",
        )
    )
    device = (
        populated_test_db.query(models.Device)
        .where(models.Device.mqtt_id == 123)
        .first()
    )
    assert device.device_type.name == "new_test_device_type_name"


def test_crud_update_device_does_not_update_last_sent_or_last_update_sent(
    populated_test_db,
):
    crud.update_device(
        schemas.DeviceReceived(
            device_type_name="test_device_type_name",
            mqtt_id=123,
            remote_name="test_remote_name",
        )
    )
    device = (
        populated_test_db.query(models.Device)
        .where(models.Device.mqtt_id == 123)
        .first()
    )
    assert device.last_update_sent == dt.fromisoformat("2025-01-01 00:00:00.000000")
    assert device.last_seen == dt.fromisoformat("2025-01-02 00:00:00.000000")
