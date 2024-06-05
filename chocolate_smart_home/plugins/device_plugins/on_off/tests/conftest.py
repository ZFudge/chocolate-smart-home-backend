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
    on_off_client_1 = models.Client(mqtt_id=123)
    on_off_client_2 = models.Client(mqtt_id=456)

    on_off_name_1 = models.DeviceName(name="Test On Device")
    on_off_name_2 = models.DeviceName(name="Test Off Device", is_server_side_name=True)

    device_type = models.DeviceType(name="on_off")

    space = models.Space(name="Main Space")

    device__id_1 = models.Device(
        online=True,
        remote_name="Test On Device - 1",
        client=on_off_client_1,
        device_type=device_type,
        device_name=on_off_name_1,
        space=space,
    )
    device__id_2 = models.Device(
        online=True,
        remote_name="Test Off Device - 2",
        client=on_off_client_2,
        device_type=device_type,
        device_name=on_off_name_2,
    )

    on_device__id_1 = OnOff(on=True, device=device__id_1)
    off_device__id_2 = OnOff(on=False, device=device__id_2)

    db = empty_test_db

    db.add(on_off_client_1)
    db.add(on_off_client_2)

    db.add(on_off_name_1)
    db.add(on_off_name_2)

    db.add(device_type)
    db.add(space)

    db.add(device__id_1)
    db.add(device__id_2)

    db.add(on_device__id_1)
    db.add(off_device__id_2)

    db.commit()

    yield db
