import pytest
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

from src import crud, models

def test_get_device_type_by_name(populated_test_db):
    device_type = crud.get_device_type_by_name("TEST_DEVICE_TYPE_NAME_1")
    assert isinstance(device_type, models.DeviceType)
    assert device_type.name == "TEST_DEVICE_TYPE_NAME_1"

def test_get_device_type_by_name_none(empty_test_db):
    assert crud.get_device_type_by_name("Non-existent Device Type Name") is None

def test_create_device_type(empty_test_db):
    device_type = crud.create_device_type("Device Type Name")
    assert isinstance(device_type, models.DeviceType)
    assert device_type.name == "Device Type Name"

def test_create_device_type_fail_on_duplicate(populated_test_db):
    with pytest.raises(IntegrityError) as e:
        crud.create_device_type("TEST_DEVICE_TYPE_NAME_1")
    assert isinstance(e.value.orig, UniqueViolation)
