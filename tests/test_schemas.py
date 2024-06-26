from chocolate_smart_home import models, schemas
from chocolate_smart_home.schemas.utils import to_schema


def test_device_to_schema(populated_test_db):
    device = (
        populated_test_db
        .query(models.Device)
        .filter(models.Device.id == 1)
        .one()
    )
    expected_schema = schemas.Device(
        id=1,
        online=True,
        reboots=0,
        remote_name="Remote Name 1 - 1",
        client=schemas.Client(id=1, mqtt_id=123),
        device_name=schemas.DeviceName(id=1, name="Test Device Name 1", is_server_side_name=False),
        device_type=schemas.DeviceType(id=1, name="TEST_DEVICE_TYPE_NAME_1"),
        space=schemas.Space(id=1, name="Main Space"),
    )
    assert to_schema(device) == expected_schema


def test_device_to_schema_empty_space(populated_test_db):
    device = (
        populated_test_db
        .query(models.Device)
        .filter(models.Device.id == 2)
        .one()
    )
    expected_schema = schemas.Device(
        id=2,
        online=False,
        reboots=0,
        remote_name="Remote Name 2 - 2",
        client=schemas.Client(id=2, mqtt_id=456),
        device_name=schemas.DeviceName(id=2, name="Test Device Name 2", is_server_side_name=True),
        device_type=schemas.DeviceType(id=2, name="TEST_DEVICE_TYPE_NAME_2"),
        space=None,
    )
    assert to_schema(device) == expected_schema


def test_to_schema_empty_schema():
    assert to_schema(None) is None

