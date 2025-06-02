import pytest

from src import models
from src.plugins.device_plugins.neo_pixel.model import NeoPixel


@pytest.fixture
def empty_test_db(empty_test_db):
    """Modifies empty_test_db fixture from ../conftest to drop NeoPixel
    rows before dropping foreign Device/DeviceType rows."""
    yield empty_test_db

    empty_test_db.query(NeoPixel).delete()
    empty_test_db.commit()


@pytest.fixture
def populated_test_db(empty_test_db):
    device_type = models.DeviceType(name="neo_pixel")

    tag = models.Tag(name="Main Tag")

    device__id_1 = models.Device(
        online=True,
        remote_name="Test Neo Pixel Device - 1",
        mqtt_id=123,
        device_type=device_type,
        name="Test Neo Pixel Device One",
        tags=[tag],
    )
    device__id_2 = models.Device(
        online=True,
        remote_name="Test Neo Pixel Device - 2",
        mqtt_id=456,
        device_type=device_type,
        name="Test Neo Pixel Device Two",
    )

    neo_pixel_device__id_1 = NeoPixel(
        on=True,
        twinkle=True,
        scheduled_palette_rotation=True,
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
        pir_armed=True,
        pir_timeout_seconds=172,
        device=device__id_1,
    )
    neo_pixel_device__id_2 = NeoPixel(
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
        device=device__id_2,
    )

    db = empty_test_db

    db.add(device_type)
    db.add(tag)

    db.add(device__id_1)
    db.add(device__id_2)

    db.add(neo_pixel_device__id_1)
    db.add(neo_pixel_device__id_2)

    db.commit()

    yield db
