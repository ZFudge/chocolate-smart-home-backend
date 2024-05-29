from chocolate_smart_home.plugins.device_plugins.on_off.model import OnOff


def test_on_off_model_str(populated_test_db):
    on_device = populated_test_db.query(OnOff).filter(OnOff.id == 1).one()
    expected_str = (
        "OnOff(id=1, device_id=1, on=True)\n"
        "Device(id=1, mqtt_id=111, name=Test On Device, remote_name=Test On Device - 1, online=True, reboots=0, device_type_id=1)\n"
        "DeviceType(id=1, name=on_off)"
    )
    assert str(on_device) == expected_str

    off_device = populated_test_db.query(OnOff).filter(OnOff.id == 2).one()
    expected_str = (
        "OnOff(id=2, device_id=2, on=False)\n"
        "Device(id=2, mqtt_id=222, name=Test Off Device, remote_name=Test Off Device - 2, online=True, reboots=0, device_type_id=1)\n"
        "DeviceType(id=1, name=on_off)"
    )
    assert str(off_device) == expected_str