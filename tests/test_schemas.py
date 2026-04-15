from src import models, schemas


def test_device_mod_obj_to_frontend_schema_with_tags(populated_test_db):
    device = (
        populated_test_db.query(models.Device).where(models.Device.mqtt_id == 123).one()
    )
    assert schemas.device_mod_obj_to_frontend_schema(device) == schemas.DeviceFrontend(
        mqtt_id=123,
        remote_name="Remote Name 1 - 1",
        name="Test Device Name 1",
        device_type_name="TEST_DEVICE_TYPE_NAME_1",
        tags=[1, 2],
        reboots=0,
        last_seen="2025-01-02 00:00:00",
        last_update_sent="2025-01-01 00:00:00",
    )


def test_device_mod_obj_to_frontend_schema_empty_tag(populated_test_db):
    device = (
        populated_test_db.query(models.Device).where(models.Device.mqtt_id == 234).one()
    )
    assert schemas.device_mod_obj_to_frontend_schema(device) == schemas.DeviceFrontend(
        mqtt_id=234,
        remote_name="Remote Name 2 - 2",
        name="Test Device Name 2",
        device_type_name="TEST_DEVICE_TYPE_NAME_2",
        tags=None,
        reboots=0,
        last_seen="2025-01-01 00:00:00",
        last_update_sent="2025-01-02 00:00:00",
    )


def test_device_mod_obj_to_frontend_schema_empty_schema():
    assert schemas.device_mod_obj_to_frontend_schema(None) is None
