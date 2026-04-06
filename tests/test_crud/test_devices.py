from datetime import datetime as dt, timedelta

import pytest
from sqlalchemy.exc import NoResultFound

from src import crud, models


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
    assert device_1.device_type.name == "TEST_DEVICE_TYPE_NAME_1"
    assert device_1.remote_name == "Remote Name 1 - 1"
    assert device_1.name == "Test Device Name 1"
    assert device_2.mqtt_id == 234
    assert device_2.device_type.name == "TEST_DEVICE_TYPE_NAME_2"
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


def test_update_last_update_sent_if_exists(populated_test_db):
    assert crud.get_device_by_id(123).last_update_sent == dt.fromisoformat(
        "2025-01-01 00:00:00.000000"
    )
    crud.update_last_update_sent_if_exists(mqtt_id=123)
    assert crud.get_device_by_id(123).last_update_sent is not None
    assert crud.get_device_by_id(123).last_update_sent > dt.now() - timedelta(seconds=1)
    assert crud.get_device_by_id(234).last_update_sent == dt.fromisoformat(
        "2025-01-02 00:00:00.000000"
    )
    crud.update_last_update_sent_if_exists(mqtt_id=234)
    assert crud.get_device_by_id(234).last_update_sent is not None
    assert crud.get_device_by_id(234).last_update_sent > dt.now() - timedelta(seconds=1)
