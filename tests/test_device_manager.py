from chocolate_smart_home import models
from chocolate_smart_home.plugins.base_device_manager import BaseDeviceManager
from chocolate_smart_home.schemas import DeviceReceived


def test_create_device(empty_test_db):
    db = empty_test_db
    device_data = DeviceReceived(
        mqtt_id=111,
        device_type_name="test_device_type",
        remote_name="Remote Name - 2",
    )
    new_device = BaseDeviceManager().create_device(device_data)
    assert new_device.id == 1
    assert new_device.online is True
    assert new_device.remote_name == "Remote Name - 2"
    assert new_device.client.mqtt_id == 111
    assert new_device.device_type.name == "test_device_type"
    assert new_device.device_name.name == "Remote Name"

    db_device = db.query(models.Device).filter(models.Device.id == new_device.id).one()
    assert db_device == new_device


def test_device_reboots(populated_test_db):
    """Assert that .reboots increments when .update_device receives a new remote_name value"""
    device_manager = BaseDeviceManager()
    orig_device_data = DeviceReceived(
        mqtt_id=123,
        device_type_name="TEST_DEVICE_TYPE_NAME_1",
        remote_name="Remote Name 1 - 1",
    )
    assert device_manager.update_device(orig_device_data).reboots == 0

    remote_name = "Remote Name 1 - 1 - 123"
    for _ in range(3):
        device_data = DeviceReceived(
            mqtt_id=orig_device_data.mqtt_id,
            device_type_name=orig_device_data.device_type_name,
            remote_name=remote_name,
        )
        device: models.Device = device_manager.update_device(device_data)
        assert device.reboots == 1

    remote_name = "Remote Name 1 - 1 - 234"
    device_data = DeviceReceived(
        mqtt_id=orig_device_data.mqtt_id,
        device_type_name=orig_device_data.device_type_name,
        remote_name=remote_name,
    )
    device: models.Device = device_manager.update_device(device_data)
    assert device.reboots == 2

    remote_name = "Remote Name 1 - 1 - 345"
    device_data = DeviceReceived(
        mqtt_id=orig_device_data.mqtt_id,
        device_type_name=orig_device_data.device_type_name,
        remote_name=remote_name,
    )
    device: models.Device = device_manager.update_device(device_data)
    assert device.reboots == 3

    remote_name = "Remote Name 1 - 1 - 456"
    for _ in range(3):
        device_data = DeviceReceived(
            mqtt_id=orig_device_data.mqtt_id,
            device_type_name=orig_device_data.device_type_name,
            remote_name=remote_name,
        )
        device: models.Device = device_manager.update_device(device_data)
        assert device.reboots == 4

    remote_name = "Remote Name 1 - 1 - 567"
    for _ in range(3):
        device_data = DeviceReceived(
            mqtt_id=orig_device_data.mqtt_id,
            device_type_name=orig_device_data.device_type_name,
            remote_name=remote_name,
        )
        device: models.Device = device_manager.update_device(device_data)
        assert device.reboots == 5


def test_device_marked_online(populated_test_db):
    """Assert that .online is True after calling .update_device"""
    client: models.Client = (
        populated_test_db.query(models.Client)
        .filter(models.Client.mqtt_id == 456)
        .one()
    )
    offline_device: models.Device = (
        populated_test_db.query(models.Device)
        .filter(models.Device.client == client)
        .one()
    )
    assert offline_device.online is False

    device_data = DeviceReceived(
        mqtt_id=456,
        device_type_name="TEST_DEVICE_TYPE_NAME_2",
        remote_name="Remote Name 2 - 2",
    )
    updated_device = BaseDeviceManager().update_device(device_data)
    assert updated_device is offline_device
    assert updated_device.online is True
