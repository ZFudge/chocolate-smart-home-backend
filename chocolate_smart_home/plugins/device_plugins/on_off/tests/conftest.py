import pytest

from chocolate_smart_home import models
from chocolate_smart_home.plugins.device_plugins.on_off.model import OnOff


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

    tag = models.Tag(name="Main Tag")

    device__id_1 = models.Device(
        mqtt_id=123,
        name="Test On Device",
        online=True,
        remote_name="Test On Device - 1",
        device_type=device_type,
        tags=[tag],
    )
    device__id_2 = models.Device(
        mqtt_id=456,
        name="Test Off Device",
        online=True,
        remote_name="Test Off Device - 2",
        device_type=device_type,
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
