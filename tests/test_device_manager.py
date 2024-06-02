from chocolate_smart_home import models
from chocolate_smart_home.plugins.base_device_manager import BaseDeviceManager


def test_device_reboots(populated_test_db):
    device_manager = BaseDeviceManager()
    orig_device_data = {
        "mqtt_id": 123,
        "device_type_name": "TEST_DEVICE_TYPE_NAME_1",
        "remote_name": "Remote Name 1",
    }

    assert device_manager.update_device(orig_device_data).reboots == 0

    remote_name = "Remote Name 1 - 123"
    for _ in range(3):
        device: models.Device = device_manager.update_device(orig_device_data | dict(remote_name=remote_name))
        assert device.reboots == 1

    remote_name = "Remote Name 1 - 234"
    device: models.Device = device_manager.update_device(orig_device_data | dict(remote_name=remote_name))
    assert device.reboots == 2

    remote_name = "Remote Name 1 - 345"
    device: models.Device = device_manager.update_device(orig_device_data | dict(remote_name=remote_name))
    assert device.reboots == 3

    remote_name = "Remote Name 1 - 456"
    for _ in range(3):
        device: models.Device = device_manager.update_device(orig_device_data | dict(remote_name=remote_name))
        assert device.reboots == 4

    remote_name = "Remote Name 1 - 567"
    for _ in range(3):
        device: models.Device = device_manager.update_device(orig_device_data | dict(remote_name=remote_name))
        assert device.reboots == 5


def test_device_marked_online(populated_test_db):
    client: models.Client = (
        populated_test_db
        .query(models.Client)
        .filter(models.Client.mqtt_id == 456)
        .one()
    )
    offline_device: models.Device = (
        populated_test_db
        .query(models.Device)
        .filter(models.Device.client == client)
        .one()
    )

    assert offline_device.online is False

    updated_device = BaseDeviceManager().update_device({
        "mqtt_id": 456,
        "device_type_name": "TEST_DEVICE_TYPE_NAME_2",
        "remote_name": "Remote Name 2",
    })

    assert updated_device is offline_device and updated_device.online is True
