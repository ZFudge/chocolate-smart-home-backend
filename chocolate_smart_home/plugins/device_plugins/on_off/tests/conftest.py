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
    on_off_device_type = models.DeviceType(name="on_off")

    device__id_1 = models.Device(
        mqtt_id=111,
        device_type=on_off_device_type,
        remote_name="Test On Device - 1",
        name="Test On Device",
        online=True,
    )
    device__id_2 = models.Device(
        mqtt_id=222,
        device_type=on_off_device_type,
        remote_name="Test Off Device - 2",
        name="Test Off Device",
        online=True,
    )

    on_device__id_1 = OnOff(on=True, device=device__id_1)
    off_device__id_2 = OnOff(on=False, device=device__id_2)

    empty_test_db.add(on_off_device_type)

    empty_test_db.add(device__id_1)
    empty_test_db.add(device__id_2)

    empty_test_db.add(on_device__id_1)
    empty_test_db.add(off_device__id_2)

    empty_test_db.commit()

    yield empty_test_db
