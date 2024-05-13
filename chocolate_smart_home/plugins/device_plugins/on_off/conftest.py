import pytest

from chocolate_smart_home import models
from chocolate_smart_home.plugins.device_plugins.on_off.model import OnOffDevice


@pytest.fixture
def test_database(test_database):
    """Modifies test_database fixture from ../conftest to drop OnOffDevice
       rows before dropping foreign Device/DeviceType rows."""
    yield test_database

    test_database.query(OnOffDevice).delete()
    test_database.commit()


@pytest.fixture
def test_data(test_database):
    device_type = models.DeviceType(name="on_off")
    device = models.Device(
        mqtt_id=111,
        device_type=device_type,
        remote_name="Remote Name 1",
        name="Name 1",
        online=True,
    )
    on_off_device = OnOffDevice(on=True, device=device)

    test_database.add(device_type)
    test_database.add(device)
    test_database.add(on_off_device)
    test_database.commit()

    yield test_database
