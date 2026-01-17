import pytest
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError, NoResultFound

from src import crud, database, models


def test_get_sqlalchemy_database_url(empty_test_db):
    sqlalchemy_database_url = database.get_sqlalchemy_database_url()
    expected_sqlalchemy_database_url = (
        "postgresql://testuser:testpw@csm-postgres-db-dev:5432/testdb"
    )
    assert sqlalchemy_database_url == expected_sqlalchemy_database_url


def test_create_device_type(empty_test_db):
    device_type = crud.create_device_type("Device Type Name")
    assert isinstance(device_type, models.DeviceType)
    assert device_type.name == "Device Type Name"


def test_create_device_type_fail_on_duplicate(empty_test_db):
    crud.create_device_type("Device Type Name")
    with pytest.raises(IntegrityError) as e:
        crud.create_device_type("Device Type Name")
    assert isinstance(e.value.orig, UniqueViolation)


def test_get_device_by_device_id(populated_test_db):
    device = crud.get_device_by_device_id(2)
    assert isinstance(device, models.Device)
    assert device.id == 2
    assert device.mqtt_id == 456
    assert device.device_type.name == "TEST_DEVICE_TYPE_NAME_2"
    assert device.remote_name == "Remote Name 2 - 2"
    assert device.name == "Test Device Name 2"


def test_get_device_by_device_id_fails_on_device_id_does_not_exist(empty_test_db):
    with pytest.raises(NoResultFound):
        crud.get_device_by_device_id(1)


def test_get_devices_by_mqtt_id(populated_test_db):
    device = crud.get_devices_by_mqtt_id(456)
    assert isinstance(device, models.Device)
    assert device.id == 2
    assert device.mqtt_id == 456
    assert device.device_type.name == "TEST_DEVICE_TYPE_NAME_2"
    assert device.remote_name == "Remote Name 2 - 2"
    assert device.name == "Test Device Name 2"


def test_get_devices_by_mqtt_id_multiple(populated_test_db):
    devices = crud.get_devices_by_mqtt_id([123, 456])
    assert isinstance(devices, list)
    assert len(devices) == 2
    assert devices[0].id == 1
    assert devices[0].mqtt_id == 123
    assert devices[0].device_type.name == "TEST_DEVICE_TYPE_NAME_1"
    assert devices[0].remote_name == "Remote Name 1 - 1"
    assert devices[0].name == "Test Device Name 1"
    assert devices[1].id == 2
    assert devices[1].mqtt_id == 456
    assert devices[1].device_type.name == "TEST_DEVICE_TYPE_NAME_2"
    assert devices[1].remote_name == "Remote Name 2 - 2"
    assert devices[1].name == "Test Device Name 2"


def test_get_devices_by_mqtt_id_fails_on_mqtt_id_does_not_exist(empty_test_db):
    with pytest.raises(NoResultFound):
        crud.get_devices_by_mqtt_id(123)


def test_get_device_fails_on_device_id_does_not_exist(empty_test_db):
    with pytest.raises(NoResultFound):
        crud.get_device_by_device_id(1)


def test_get_all_devices_data_empty(empty_test_db):
    assert crud.get_all_devices_data() == []


def test_get_all_devices_data(populated_test_db):
    devices = crud.get_all_devices_data()
    assert len(devices) == 2

    device_1, device_2 = devices

    assert device_1.id == 1
    assert device_1.mqtt_id == 123
    assert device_1.device_type.name == "TEST_DEVICE_TYPE_NAME_1"
    assert device_1.remote_name == "Remote Name 1 - 1"
    assert device_1.name == "Test Device Name 1"

    assert device_2.id == 2
    assert device_2.mqtt_id == 456
    assert device_2.device_type.name == "TEST_DEVICE_TYPE_NAME_2"
    assert device_2.remote_name == "Remote Name 2 - 2"
    assert device_2.name == "Test Device Name 2"


def test_delete_device(populated_test_db):
    crud.delete_device(device_id=1)
    assert len(crud.get_all_devices_data()) == 1
    crud.delete_device(device_id=2)
    assert len(crud.get_all_devices_data()) == 0


def test_delete_device_fails_on_device_does_not_exists(empty_test_db):
    with pytest.raises(NoResultFound):
        crud.delete_device(device_id=1)
