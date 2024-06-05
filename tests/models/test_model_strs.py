from chocolate_smart_home import models


def test_device_model_str(populated_test_db):
    device_1 = (
        populated_test_db
        .query(models.Device)
        .filter(models.Device.id == 1)
        .one()
    )
    expected_str_1 = (
        "Device(id=1, remote_name=Remote Name 1 - 1, online=True, reboots=0, client_id=1, device_name_id=1, device_type_id=1)\n"
        "DeviceName(id=1, name=Test Device Name 1, is_server_side_name=False)\n"
        "Client(id=1, mqtt_id=123)\n"
        "DeviceType(id=1, name=TEST_DEVICE_TYPE_NAME_1)"
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
        "Device(id=2, remote_name=Remote Name 2 - 2, online=False, reboots=0, client_id=2, device_name_id=2, device_type_id=2)\n"
        "DeviceName(id=2, name=Test Device Name 2, is_server_side_name=True)\n"
        "Client(id=2, mqtt_id=456)\n"
        "DeviceType(id=2, name=TEST_DEVICE_TYPE_NAME_2)"
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


def test_device_name_model_str(populated_test_db):
    device_name_1 = (
        populated_test_db
        .query(models.DeviceName)
        .filter(models.DeviceName.id == 1)
        .one()
    )
    expected_str_1 = "DeviceName(id=1, name=Test Device Name 1, is_server_side_name=False)"
    assert str(device_name_1) == expected_str_1
    assert repr(device_name_1) == expected_str_1

    device_name_2 = (
        populated_test_db
        .query(models.DeviceName)
        .filter(models.DeviceName.id == 2)
        .one()
    )
    expected_str_2 = "DeviceName(id=2, name=Test Device Name 2, is_server_side_name=True)"
    assert str(device_name_2) == expected_str_2
    assert repr(device_name_2) == expected_str_2


def test_client_model_str(populated_test_db):
    client_1 = (
        populated_test_db
        .query(models.Client)
        .filter(models.Client.id == 1)
        .one()
    )
    expected_str_1 = "Client(id=1, mqtt_id=123)"
    assert str(client_1) == expected_str_1
    assert repr(client_1) == expected_str_1

    client_2 = (
        populated_test_db
        .query(models.Client)
        .filter(models.Client.id == 2)
        .one()
    )
    expected_str_2 = "Client(id=2, mqtt_id=456)"
    assert str(client_2) == expected_str_2
    assert repr(client_2) == expected_str_2
