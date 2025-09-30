import pydantic
import pytest

from src import schemas
from src.plugins.device_plugins.neo_pixel import (
    model,
    schemas as neo_pixel_schemas,
    utils,
)


def test_to_neo_pixel_schema(populated_test_db):
    device = (
        populated_test_db.query(model.NeoPixel).filter(model.NeoPixel.id == 1).one()
    )
    expected_schema = neo_pixel_schemas.NeoPixelDevice(
        id=1,
        on=True,
        twinkle=True,
        transform=True,
        ms=5,
        brightness=255,
        palette=[
            "#000102",
            "#030405",
            "#060708",
            "#090a0b",
            "#0c0d0e",
            "#0f1011",
            "#121314",
            "#d2dce6",
            "#f0faff",
        ],
        pir=neo_pixel_schemas.PIR(armed=True, timeout=172),
        device=schemas.Device(
            id=1,
            online=True,
            reboots=0,
            remote_name="Test Neo Pixel Device - 1",
            mqtt_id=123,
            name="Test Neo Pixel Device One",
            device_type=schemas.DeviceType(id=1, name="neo_pixel"),
            tags=[schemas.Tag(id=1, name="NeoPixel Tag")],
        ),
    )
    assert utils.to_neo_pixel_schema(device) == expected_schema


def test_to_neo_pixel_schema_no_tag(populated_test_db):
    device = (
        populated_test_db.query(model.NeoPixel).filter(model.NeoPixel.id == 2).one()
    )
    expected_schema = neo_pixel_schemas.NeoPixelDevice(
        id=2,
        on=False,
        twinkle=True,
        transform=False,
        ms=55,
        brightness=123,
        palette=[
            "#000102",
            "#030405",
            "#060708",
            "#090a0b",
            "#0c0d0e",
            "#0f1011",
            "#121314",
            "#d2dce6",
            "#f0faff",
        ],
        pir=None,
        device=schemas.Device(
            id=2,
            mqtt_id=456,
            name="Test Neo Pixel Device Two",
            remote_name="Test Neo Pixel Device - 2",
            device_type=schemas.DeviceType(id=1, name="neo_pixel"),
            tags=None,
            online=True,
            reboots=0,
        ),
    )
    assert utils.to_neo_pixel_schema(device) == expected_schema


def test_palette_validator_length_short(populated_test_db):
    with pytest.raises(pydantic.ValidationError):
        neo_pixel_schemas.NeoPixelOptions(
            palette=[
                "#000000",
                "#000000",
                "#000000",
                "#000000",
                "#000000",
                "#000000",
                "#000000",
                "#000000",
                # Missing 9th row
            ]
        )


def test_palette_validator_length_long(populated_test_db):
    with pytest.raises(pydantic.ValidationError):
        neo_pixel_schemas.NeoPixelOptions(
            palette=[
                "#000000",
                "#000000",
                "#000000",
                "#000000",
                "#000000",
                "#000000",
                "#000000",
                "#000000",
                "#000000",
                # 10th row
                "#000000",
            ]
        )


def test_palette_validator_invalid_color_10th_color(populated_test_db):
    with pytest.raises(pydantic.ValidationError):
        neo_pixel_schemas.NeoPixelOptions(
            palette=["#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000"]
        )


def test_palette_validator_invalid_color_format_missing_digit(populated_test_db):
    with pytest.raises(pydantic.ValidationError):
        neo_pixel_schemas.NeoPixelOptions(
            palette=["#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#00000"]
        )


def test_palette_validator_invalid_color_format_missing_pound_sign(populated_test_db):
    with pytest.raises(pydantic.ValidationError):
        neo_pixel_schemas.NeoPixelOptions(
            palette=["#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "0000000"]
        )


def test_palette_validator_invalid_color_format_digit_out_of_range(populated_test_db):
    with pytest.raises(pydantic.ValidationError):
        neo_pixel_schemas.NeoPixelOptions(
            palette=["#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#00000g"]
        )
