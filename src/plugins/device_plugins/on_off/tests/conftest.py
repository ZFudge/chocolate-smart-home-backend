import pytest
from datetime import datetime as dt

from src import models
from src.plugins.device_plugins.on_off.model import OnOff


OLDER_DATE = dt.fromisoformat("2025-01-01 00:00:00.000000")
NEWER_DATE = dt.fromisoformat("2025-01-02 00:00:00.000000")


@pytest.fixture
def empty_test_db(empty_test_db):
    """Modifies empty_test_db fixture from ../conftest to drop OnOff
    rows before dropping foreign Device/DeviceType rows."""
    yield empty_test_db

    empty_test_db.query(OnOff).delete()
    empty_test_db.commit()


@pytest.fixture
def populated_test_db(empty_test_db):
    device_type = models.DeviceType(name="on_off")

    tag = models.Tag(name="OnOff Tag")

    device__id_1 = models.Device(
        mqtt_id=123,
        name="Test On Device",
        remote_name="Test On Device - 1",
        device_type=device_type,
        tags=[tag],
        last_seen=NEWER_DATE,
        last_update_sent=OLDER_DATE,
    )
    device__id_2 = models.Device(
        mqtt_id=456,
        name="Test Off Device",
        remote_name="Test Off Device - 2",
        device_type=device_type,
        last_seen=OLDER_DATE,
        last_update_sent=NEWER_DATE,
    )

    on_device__id_1 = OnOff(on=True, device=device__id_1)
    off_device__id_2 = OnOff(on=False, device=device__id_2)

    db = empty_test_db

    db.add(device_type)
    db.add(tag)

    db.add(device__id_1)
    db.add(device__id_2)

    db.add(on_device__id_1)
    db.add(off_device__id_2)

    db.commit()

    yield db
