from src import models


def test_device_model_str(populated_test_db):
    device_1 = (
        populated_test_db.query(models.Device)
        .filter(models.Device.mqtt_id == 123)
        .one()
    )
    assert str(device_1) == (
        "Device("
        "mqtt_id=123, "
        "last_seen=2025-01-02 00:00:00, "
        "last_update_sent=2025-01-01 00:00:00, "
        "reboots=0, "
        "remote_name=Remote Name 1 - 1, "
        "name=Test Device Name 1, "
        "device_type_name=TEST_DEVICE_TYPE_NAME_1, "
        "tags=[Main Tag, Other Tag])"
    )
    assert repr(device_1) == str(device_1)

    device_2 = (
        populated_test_db.query(models.Device)
        .filter(models.Device.mqtt_id == 234)
        .one()
    )
    assert str(device_2) == (
        "Device("
        "mqtt_id=234, "
        "last_seen=2025-01-01 00:00:00, "
        "last_update_sent=2025-01-02 00:00:00, "
        "reboots=0, "
        "remote_name=Remote Name 2 - 2, "
        "name=Test Device Name 2, "
        "device_type_name=TEST_DEVICE_TYPE_NAME_2, "
        "tags=null)"
    )
    assert repr(device_2) == str(device_2)


def test_device_type_model_str(populated_test_db):
    device_type_1 = (
        populated_test_db.query(models.DeviceType)
        .filter(models.DeviceType.id == 1)
        .one()
    )
    expected_str_1 = "DeviceType(id=1, name=TEST_DEVICE_TYPE_NAME_1)"
    assert str(device_type_1) == expected_str_1
    assert repr(device_type_1) == expected_str_1

    device_type_2 = (
        populated_test_db.query(models.DeviceType)
        .filter(models.DeviceType.id == 2)
        .one()
    )
    expected_str_2 = "DeviceType(id=2, name=TEST_DEVICE_TYPE_NAME_2)"
    assert str(device_type_2) == expected_str_2
    assert repr(device_type_2) == expected_str_2


def test_tag_model_str(populated_test_db):
    tag_1 = populated_test_db.query(models.Tag).filter(models.Tag.id == 1).one()
    expected_str_1 = "Tag(id=1, name=Main Tag)"
    assert str(tag_1) == expected_str_1
    assert repr(tag_1) == expected_str_1

    tag_2 = populated_test_db.query(models.Tag).filter(models.Tag.id == 2).one()
    expected_str_2 = "Tag(id=2, name=Other Tag)"
    assert str(tag_2) == expected_str_2
    assert repr(tag_2) == expected_str_2
