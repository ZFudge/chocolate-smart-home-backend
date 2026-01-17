from src import models, schemas
from src.schemas.utils import to_schema


def test_device_to_schema_with_tags(populated_test_db):
    device = populated_test_db.query(models.Device).filter(models.Device.id == 1).one()
    expected_schema = schemas.Device(
        id=1,
        online=True,
        reboots=0,
        mqtt_id=123,
        name="Test Device Name 1",
        remote_name="Remote Name 1 - 1",
        device_type=schemas.DeviceType(id=1, name="TEST_DEVICE_TYPE_NAME_1"),
        tags=[
            schemas.Tag(id=1, name="Main Tag"),
            schemas.Tag(id=2, name="Other Tag"),
        ],
    )

    assert to_schema(device) == expected_schema


def test_device_to_schema_empty_tag(populated_test_db):
    device = populated_test_db.query(models.Device).filter(models.Device.id == 2).one()
    expected_schema = schemas.Device(
        id=2,
        reboots=0,
        remote_name="Remote Name 2 - 2",
        mqtt_id=456,
        name="Test Device Name 2",
        device_type=schemas.DeviceType(id=2, name="TEST_DEVICE_TYPE_NAME_2"),
        tags=None,
    )

    assert to_schema(device) == expected_schema


def test_to_schema_empty_schema():
    assert to_schema(None) is None
