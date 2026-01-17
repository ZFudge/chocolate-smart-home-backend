import pytest
from datetime import datetime as dt

from src import models
from src.plugins.device_plugins.neo_pixel.model import NeoPixel, Palette


OLDER_DATE = dt.fromisoformat("2025-01-01 00:00:00.000000")
NEWER_DATE = dt.fromisoformat("2025-01-02 00:00:00.000000")


@pytest.fixture
def empty_test_db(empty_test_db):
    """Modifies empty_test_db fixture from ../conftest to drop NeoPixel
    rows before dropping foreign Device/DeviceType rows."""
    yield empty_test_db

    empty_test_db.query(NeoPixel).delete()
    empty_test_db.query(Palette).delete()
    empty_test_db.commit()


@pytest.fixture
def populated_test_db(empty_test_db):
    device_type = models.DeviceType(name="neo_pixel")

    tag = models.Tag(name="NeoPixel Tag")

    device__id_1 = models.Device(
        remote_name="Test Neo Pixel Device - 1",
        mqtt_id=123,
        device_type=device_type,
        name="Test Neo Pixel Device One",
        last_seen=NEWER_DATE,
        last_update_sent=OLDER_DATE,
    )
    device__id_1.tags.append(tag)

    device__id_2 = models.Device(
        remote_name="Test Neo Pixel Device - 2",
        mqtt_id=456,
        device_type=device_type,
        name="Test Neo Pixel Device Two",
        last_seen=NEWER_DATE,
        last_update_sent=OLDER_DATE,
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
        armed=True,
        timeout=172,
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

    palette = Palette(
        name="Test Palette",
        palette=[
            0,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
        ],
    )
    db.add(palette)

    db.commit()

    yield db
