import pytest

from chocolate_smart_home import models
from chocolate_smart_home.plugins.device_plugins.on_off.model import OnOff


@pytest.fixture
def test_database(test_database):
    """Modifies test_database fixture from ../conftest to drop OnOff
    rows before dropping foreign Device/DeviceType rows."""
    yield test_database

    test_database.query(OnOff).delete()
    test_database.commit()


@pytest.fixture
def test_data(test_database):
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

    test_database.add(on_off_device_type)

    test_database.add(device__id_1)
    test_database.add(device__id_2)

    test_database.add(on_device__id_1)
    test_database.add(off_device__id_2)

    test_database.commit()

    yield test_database
