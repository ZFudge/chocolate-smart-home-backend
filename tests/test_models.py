from chocolate_smart_home import models


def test_device_model_str(populated_test_db):
    device_1 = (
        populated_test_db
        .query(models.Device)
        .filter(models.Device.id == 1)
        .one()
    )
    expected_str_1 = (
        "Device(id=1, remote_name=Remote Name 1, online=True, reboots=0, client_id=1, device_type_id=1, device_name_id=1)\n"
        "DeviceName(id=1, name=Test Device Name 1)\n"
        "Client(id=1, mqtt_id=123)\n"
        "DeviceType(id=1, name=TEST_DEVICE_TYPE_NAME_1)"
    )
    assert str(device_1) == expected_str_1

    device_2 = (
        populated_test_db
        .query(models.Device)
        .filter(models.Device.id == 2)
        .one()
    )
    expected_str_2 = (
        "Device(id=2, remote_name=Remote Name 2, online=False, reboots=0, client_id=2, device_type_id=2, device_name_id=2)\n"
        "DeviceName(id=2, name=Test Device Name 2)\n"
        "Client(id=2, mqtt_id=456)\n"
        "DeviceType(id=2, name=TEST_DEVICE_TYPE_NAME_2)"
    )
    assert str(device_2) == expected_str_2


def test_device_type_model_str(populated_test_db):
    device_type_1 = (
        populated_test_db
        .query(models.DeviceType)
        .filter(models.DeviceType.id == 1)
        .one()
    )
    expected_str_1 = "DeviceType(id=1, name=TEST_DEVICE_TYPE_NAME_1)"
    assert str(device_type_1) == expected_str_1

    device_type_2 = (
        populated_test_db
        .query(models.DeviceType)
        .filter(models.DeviceType.id == 2)
        .one()
    )
    expected_str_2 = "DeviceType(id=2, name=TEST_DEVICE_TYPE_NAME_2)"
    assert str(device_type_2) == expected_str_2
