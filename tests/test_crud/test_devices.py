from datetime import datetime as dt

import pytest
from sqlalchemy.exc import NoResultFound

from src import crud, models, schemas


def test_get_device_by_id(populated_test_db):
    device = crud.get_device_by_id(234)
    assert isinstance(device, models.Device)
    assert device.mqtt_id == 234
    assert device.device_type.name == "TEST_DEVICE_TYPE_NAME_2"
    assert device.remote_name == "Remote Name 2 - 2"
    assert device.name == "Test Device Name 2"


def test_get_device_by_id_none(empty_test_db):
    assert crud.get_device_by_id(123) is None


def test_get_devices_empty(empty_test_db):
    assert crud.get_devices() == ()


def test_get_devices(populated_test_db):
    devices = crud.get_devices()
    assert len(devices) == 2
    device_1, device_2 = devices
    assert device_1.mqtt_id == 123
    assert device_1.device_type_name == "TEST_DEVICE_TYPE_NAME_1"
    assert device_1.remote_name == "Remote Name 1 - 1"
    assert device_1.name == "Test Device Name 1"
    assert device_2.mqtt_id == 234
    assert device_2.device_type_name == "TEST_DEVICE_TYPE_NAME_2"
    assert device_2.remote_name == "Remote Name 2 - 2"
    assert device_2.name == "Test Device Name 2"


def test_delete_device(populated_test_db):
    crud.delete_device(mqtt_id=123)
    assert len(crud.get_devices()) == 1
    crud.delete_device(mqtt_id=234)
    assert len(crud.get_devices()) == 0


def test_delete_device_fails_on_device_does_not_exists(empty_test_db):
    with pytest.raises(NoResultFound):
        crud.delete_device(mqtt_id=123)


def test_create_device_creates_a_new_device(empty_test_db):
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


def test_create_device_does_not_set_last_seen_or_last_update_sent_values(empty_test_db):
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


def test_create_device_initializes_reboots_with_zero_value(empty_test_db):
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


def test_create_device_sets_created_date(empty_test_db):
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


def test_update_device_sets_remote_name(populated_test_db):
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


def test_update_device_increments_reboots_when_remote_name_changed(populated_test_db):
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


def test_update_device_does_not_increment_reboots_when_remote_name_not_changed(
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


def test_update_device_can_change_device_type(populated_test_db):
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


def test_update_device_does_not_update_last_sent_or_last_update_sent(populated_test_db):
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
