import pytest
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

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
