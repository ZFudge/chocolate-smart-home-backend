from chocolate_smart_home import schemas
from chocolate_smart_home.plugins.device_plugins.on_off import (
    model,
    schemas as on_off_schemas,
    utils,
)


def test_to_on_off_schema(populated_test_db):
    device = (
        populated_test_db
        .query(model.OnOff)
        .filter(model.OnOff.id == 1)
        .one()
    )
    expected_schema = on_off_schemas.OnOffDevice(
        id=1,
        on=True,
        device=schemas.Device(
            id=1,
            online=True,
            reboots=0,
            remote_name="Test On Device - 1",
            mqtt_id=123,
            name="Test On Device",
            device_type=schemas.DeviceType(id=1, name="on_off"),
            space=schemas.Space(id=1, name="Main Space"),
        ),
    )
    assert utils.to_on_off_schema(device) == expected_schema


def test_to_on_off_schema_no_space(populated_test_db):
    device = (
        populated_test_db
        .query(model.OnOff)
        .filter(model.OnOff.id == 2)
        .one()
    )
    expected_schema = on_off_schemas.OnOffDevice(
        id=2,
        on=False,
        device=schemas.Device(
            id=2,
            online=True,
            reboots=0,
            remote_name="Test Off Device - 2",
            mqtt_id=456,
            name="Test Off Device",
            device_type=schemas.DeviceType(id=1, name="on_off"),
            space=None,
        ),
    )
    assert utils.to_on_off_schema(device) == expected_schema
