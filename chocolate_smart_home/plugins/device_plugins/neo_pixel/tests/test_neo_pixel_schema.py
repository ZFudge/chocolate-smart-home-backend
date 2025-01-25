import pytest
import pydantic

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
        palette=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26],
        pir=neo_pixel_schemas.PIR(armed=True, timeout_seconds=172),
        device=schemas.Device(
            id=1,
            online=True,
            reboots=0,
            remote_name="Test Neo Pixel Device - 1",
            mqtt_id=123,
            name="Test Neo Pixel Device One",
            device_type=schemas.DeviceType(id=1, name="neo_pixel"),
            space=schemas.Space(id=1, name="Main Space"),
        ),
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
        palette=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26],
        pir=None,
        device=schemas.Device(
            id=2,
            mqtt_id=456,
            name="Test Neo Pixel Device Two",
            remote_name="Test Neo Pixel Device - 2",
            device_type=schemas.DeviceType(id=1, name="neo_pixel"),
            space=None,
            online=True,
            reboots=0,
        ),
    )
    assert utils.to_neo_pixel_schema(device) == expected_schema


def test_palette_validator_length_short(populated_test_db):
    with pytest.raises(pydantic.ValidationError):
        neo_pixel_schemas.NeoPixelOptions(palette=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])


def test_palette_validator_length_long(populated_test_db):
    with pytest.raises(pydantic.ValidationError):
        neo_pixel_schemas.NeoPixelOptions(palette=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])


def test_palette_validator_values(populated_test_db):
    with pytest.raises(pydantic.ValidationError):
        neo_pixel_schemas.NeoPixelOptions(palette=[256,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    with pytest.raises(pydantic.ValidationError):
        neo_pixel_schemas.NeoPixelOptions(palette=[-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
