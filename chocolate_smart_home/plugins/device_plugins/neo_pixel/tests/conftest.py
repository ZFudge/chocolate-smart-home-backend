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
    neo_pixel_client_1 = models.Client(mqtt_id=123)
    neo_pixel_client_2 = models.Client(mqtt_id=456)

    neo_pixel_name_1 = models.DeviceName(name="Test Neo Pixel Device One")
    neo_pixel_name_2 = models.DeviceName(name="Test Neo Pixel Device Two", is_server_side_name=True)

    device_type = models.DeviceType(name="neo_pixel")

    space = models.Space(name="Main Space")

    device__id_1 = models.Device(
        online=True,
        remote_name="Test Neo Pixel Device - 1",
        client=neo_pixel_client_1,
        device_type=device_type,
        device_name=neo_pixel_name_1,
        space=space,
    )
    device__id_2 = models.Device(
        online=True,
        remote_name="Test Neo Pixel Device - 2",
        client=neo_pixel_client_2,
        device_type=device_type,
        device_name=neo_pixel_name_2,
    )

    neo_pixel_device__id_1 = NeoPixel(
        on=True,
        twinkle=True,
        all_twinkle_colors_are_current=True,
        transform=True,
        ms=5,
        brightness=255,
        palette=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26],
        pir_armed=True,
        pir_timeout_seconds=172,
        device=device__id_1,
    )
    neo_pixel_device__id_2 = NeoPixel(
        on=False,
        twinkle=True,
        all_twinkle_colors_are_current=False,
        transform=False,
        ms=55,
        brightness=123,
        palette=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26],
        device=device__id_2,
    )

    db = empty_test_db

    db.add(neo_pixel_client_1)
    db.add(neo_pixel_client_2)

    db.add(neo_pixel_name_1)
    db.add(neo_pixel_name_2)

    db.add(device_type)
    db.add(space)

    db.add(device__id_1)
    db.add(device__id_2)

    db.add(neo_pixel_device__id_1)
    db.add(neo_pixel_device__id_2)

    db.commit()

    yield db
