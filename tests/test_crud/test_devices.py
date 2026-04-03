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

def test_get_all_devices_data_empty(empty_test_db):
    assert crud.get_all_devices_data() == []

def test_get_all_devices_data(populated_test_db):
    devices = crud.get_all_devices_data()
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
    assert len(crud.get_all_devices_data()) == 1
    crud.delete_device(mqtt_id=234)
    assert len(crud.get_all_devices_data()) == 0

def test_delete_device_fails_on_device_does_not_exists(empty_test_db):
    with pytest.raises(NoResultFound):
        crud.delete_device(mqtt_id=123)
