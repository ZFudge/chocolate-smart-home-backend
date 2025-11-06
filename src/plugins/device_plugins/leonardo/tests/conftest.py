import pytest

from src import models


@pytest.fixture
def populated_test_db(empty_test_db):
    device_type = models.DeviceType(name="leonardo")

    tag_1 = models.Tag(name="Leonardo Client 1 Tag")
    tag_2 = models.Tag(name="Leonardo Client 2 Tag")

    device__id_1 = models.Device(
        mqtt_id=123,
        name="Test Leonardo Client 1",
        online=True,
        remote_name="Test Leonardo Client 1 - 1",
        device_type=device_type,
        tags=[tag_1],
    )
    device__id_2 = models.Device(
        mqtt_id=456,
        name="Test Leonardo Client 2",
        online=True,
        remote_name="Test Leonardo Client 2 - 2",
        device_type=device_type,
        tags=[tag_2],
    )

    db = empty_test_db

    db.add(device_type)
    db.add(tag_1)
    db.add(tag_2)
    db.add(device__id_1)
    db.add(device__id_2)
    db.commit()

    yield db
