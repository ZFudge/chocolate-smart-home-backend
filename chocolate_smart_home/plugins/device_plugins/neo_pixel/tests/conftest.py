import pytest

from chocolate_smart_home import models
from chocolate_smart_home.plugins.device_plugins.neo_pixel.model import NeoPixel


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
        tag=tag,
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
        transform=True,
        ms=5,
        brightness=255,
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
