import pytest
from datetime import datetime as dt

from src import models

OLDER_DATE = dt.fromisoformat("2025-01-01 00:00:00.000000")
NEWER_DATE = dt.fromisoformat("2025-01-02 00:00:00.000000")


@pytest.fixture
def populated_test_db(empty_test_db):
    device_type = models.DeviceType(name="leonardo")

    tag_1 = models.Tag(name="Leonardo Client 1 Tag")
    tag_2 = models.Tag(name="Leonardo Client 2 Tag")

    device__id_1 = models.Device(
        mqtt_id=123,
        name="Test Leonardo Client 1",
        remote_name="Test Leonardo Client 1 - 1",
        device_type=device_type,
        tags=[tag_1],
        last_seen=NEWER_DATE,
        last_update_sent=OLDER_DATE,
    )
    device__id_2 = models.Device(
        mqtt_id=456,
        name="Test Leonardo Client 2",
        remote_name="Test Leonardo Client 2 - 2",
        device_type=device_type,
        tags=[tag_2],
        last_seen=NEWER_DATE,
        last_update_sent=OLDER_DATE,
    )

    db = empty_test_db

    db.add(device_type)
    db.add(tag_1)
    db.add(tag_2)
    db.add(device__id_1)
    db.add(device__id_2)
    db.commit()

    yield db
