from chocolate_smart_home import models


def test_device_model_str(populated_test_db):
    device_1 = (
        populated_test_db
        .query(models.Device)
        .filter(models.Device.id == 1)
        .one()
    )
    expected_str_1 = (
        'Device(id=1, mqtt_id=123, online=True, reboots=0, remote_name=Remote Name 1 - 1, name=Test Device Name 1, device_type_id=1, space_id=1)\n'
        'DeviceType(id=1, name=TEST_DEVICE_TYPE_NAME_1)\n'
        'Space(id=1, name=Main Space)'
    )
    assert str(device_1) == expected_str_1
    assert repr(device_1) == expected_str_1

    device_2 = (
        populated_test_db
        .query(models.Device)
        .filter(models.Device.id == 2)
        .one()
    )
    expected_str_2 = (
        "Device(id=2, mqtt_id=456, online=False, reboots=0, remote_name=Remote Name 2 - 2, name=Test Device Name 2, device_type_id=2, space_id=None)\n"
        "DeviceType(id=2, name=TEST_DEVICE_TYPE_NAME_2)\n"
        "Space=None"
    )
    assert str(device_2) == expected_str_2
    assert repr(device_2) == expected_str_2


def test_device_type_model_str(populated_test_db):
    device_type_1 = (
        populated_test_db
        .query(models.DeviceType)
        .filter(models.DeviceType.id == 1)
        .one()
    )
    expected_str_1 = "DeviceType(id=1, name=TEST_DEVICE_TYPE_NAME_1)"
    assert str(device_type_1) == expected_str_1
    assert repr(device_type_1) == expected_str_1

    device_type_2 = (
        populated_test_db
        .query(models.DeviceType)
        .filter(models.DeviceType.id == 2)
        .one()
    )
    expected_str_2 = "DeviceType(id=2, name=TEST_DEVICE_TYPE_NAME_2)"
    assert str(device_type_2) == expected_str_2
    assert repr(device_type_2) == expected_str_2


def test_space_model_str(populated_test_db):
    space_1 = (
        populated_test_db
        .query(models.Space)
        .filter(models.Space.id == 1)
        .one()
    )
    expected_str_1 = "Space(id=1, name=Main Space)"
    assert str(space_1) == expected_str_1
    assert repr(space_1) == expected_str_1

    space_2 = (
        populated_test_db
        .query(models.Space)
        .filter(models.Space.id == 2)
        .one()
    )
    expected_str_2 = "Space(id=2, name=Other Space)"
    assert str(space_2) == expected_str_2
    assert repr(space_2) == expected_str_2
