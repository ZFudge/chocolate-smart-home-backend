from chocolate_smart_home import schemas
from chocolate_smart_home.plugins.device_plugins.neo_pixel import (
    model,
    schemas as neo_pixel_schemas,
    utils,
)


def test_to_neo_pixel_schema(populated_test_db):
    device = (
        populated_test_db
        .query(model.NeoPixel)
        .filter(model.NeoPixel.id == 1)
        .one()
    )
    expected_schema = neo_pixel_schemas.NeoPixelDevice(
        id=1,
        on=True,
        twinkle=True,
        transform=True,
        ms=5,
        brightness=255,
        device=schemas.Device(
            id=1,
            online=True,
            reboots=0,
            remote_name="Test Neo Pixel Device - 1",
            client=schemas.Client(id=1, mqtt_id=123),
            device_name=schemas.DeviceName(id=1, name="Test Neo Pixel Device One", is_server_side_name=False),
            device_type=schemas.DeviceType(id=1, name="neo_pixel"),
            space=schemas.Space(id=1, name="Main Space"),
        )
    )
    assert utils.to_neo_pixel_schema(device) == expected_schema


def test_to_neo_pixel_schema_no_space(populated_test_db):
    device = (
        populated_test_db
        .query(model.NeoPixel)
        .filter(model.NeoPixel.id == 2)
        .one()
    )
    expected_schema = neo_pixel_schemas.NeoPixelDevice(
        id=2,
        on=False,
        twinkle=True,
        transform=False,
        ms=55,
        brightness=123,
        device=schemas.Device(
            id=2,
            online=True,
            reboots=0,
            remote_name="Test Neo Pixel Device - 2",
            client=schemas.Client(id=2, mqtt_id=456),
            device_name=schemas.DeviceName(id=2, name="Test Neo Pixel Device Two", is_server_side_name=True),
            device_type=schemas.DeviceType(id=1, name="neo_pixel"),
            space=None,
        )
    )
    assert utils.to_neo_pixel_schema(device) == expected_schema
