from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError, NoResultFound
import pytest

from chocolate_smart_home import crud, models


def test_create_device_type(test_database):
    device_type = crud.create_device_type("Device Type Name")

    assert isinstance(device_type, models.DeviceType)
    assert device_type.name == "Device Type Name"


def test_create_device_type_fail_on_duplicate(test_database):
    crud.create_device_type("Device Type Name")
    with pytest.raises(IntegrityError) as e:
        crud.create_device_type("Device Type Name")

    assert isinstance(e.value.orig, UniqueViolation)


def test_create_device(test_database):
    device = crud.create_device(
        "123",
        "Device Type Name",
        "Device Name",
        ""
    )

    assert isinstance(device, models.Device)
    assert device.mqtt_id == 123
    assert device.remote_name == "Device Name"
    assert device.device_type.name == "Device Type Name"
    assert device.name == ""
    assert device.online is True


def test_create_device_fail_on_duplicate_mqtt_id(test_database):
    crud.create_device(
        "123",
        "Device Type Name 1",
        "Device Name 1",
        ""
    )
    with pytest.raises(IntegrityError) as e:
        crud.create_device(
            "123",
            "Device Type Name 2",
            "Device Name 2",
            ""
        )

    assert isinstance(e.value.orig, UniqueViolation)


def test_get_device_by_device_id(test_data):
    device = crud.get_device_by_device_id(2)

    assert isinstance(device, models.Device)
    assert device.id == 2
    assert device.mqtt_id == 222
    assert device.device_type.name == "TEST_DEVICE_TYPE_NAME_2"
    assert device.remote_name == "Remote Name 2"
    assert device.name == "Name 2"
    assert device.online is False


def test_get_device_by_device_id_fails_on_device_id_does_not_exist(test_database):
    with pytest.raises(NoResultFound):
        crud.get_device_by_device_id(1)


def test_get_device_by_mqtt_id(test_data):
    device = crud.get_device_by_mqtt_id(222)

    assert isinstance(device, models.Device)
    assert device.id == 2
    assert device.mqtt_id == 222
    assert device.device_type.name == "TEST_DEVICE_TYPE_NAME_2"
    assert device.remote_name == "Remote Name 2"
    assert device.name == "Name 2"
    assert device.online is False


def test_get_device_by_mqtt_id_fails_on_mqtt_id_does_not_exist(test_database):
    with pytest.raises(NoResultFound):
        crud.get_device_by_mqtt_id(111)


def test_update_device(test_data):
    device = crud.get_device_by_device_id(2)

    assert isinstance(device, models.Device)
    assert device.id == 2
    assert device.mqtt_id == 222
    assert device.device_type.name == "TEST_DEVICE_TYPE_NAME_2"
    assert device.remote_name == "Remote Name 2"
    assert device.name == "Name 2"
    assert device.online is False

    device_updated = crud.update_device(
        "222",
        "TEST_DEVICE_TYPE_NAME_NEW",
        "New Remote Name",
        "New Name"
    )

    assert isinstance(device_updated, models.Device)
    assert device_updated.id == 2
    assert device_updated.mqtt_id == 222
    assert device_updated.device_type.name == "TEST_DEVICE_TYPE_NAME_NEW"
    assert device_updated.remote_name == "New Remote Name"
    assert device_updated.name == "New Name"
    assert device_updated.online is True


def test_update_device_fails_on_device_id_does_not_exist(test_database):
    with pytest.raises(NoResultFound):
        crud.get_device_by_device_id(1)


def test_get_all_devices_data_empty(test_database):
    assert crud.get_all_devices_data(test_database) == []


def test_get_all_devices_data(test_database, test_data):
    devices = crud.get_all_devices_data(test_database)

    assert len(devices) == 2

    [device_1, device_2] = devices

    assert device_1.id == 1
    assert device_1.mqtt_id == 111
    assert device_1.device_type.name == "TEST_DEVICE_TYPE_NAME_1"
    assert device_1.remote_name == "Remote Name 1"
    assert device_1.name == "Name 1"
    assert device_1.online is True

    assert device_2.id == 2
    assert device_2.mqtt_id == 222
    assert device_2.device_type.name == "TEST_DEVICE_TYPE_NAME_2"
    assert device_2.remote_name == "Remote Name 2"
    assert device_2.name == "Name 2"
    assert device_2.online is False


def test_delete_device(test_database, test_data):
    crud.delete_device(test_database, 1)

    assert len(crud.get_all_devices_data(test_database)) == 1

    crud.delete_device(test_database, 2)

    assert len(crud.get_all_devices_data(test_database)) == 0


def test_delete_device_fails_on_device_does_not_exists(test_database):
    with pytest.raises(NoResultFound):
        crud.delete_device(test_database, 1)
