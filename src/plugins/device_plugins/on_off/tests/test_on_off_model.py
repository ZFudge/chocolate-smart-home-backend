from src.plugins.device_plugins.on_off.model import OnOff


def test_on_off_model_str(populated_test_db):
    on_device = populated_test_db.query(OnOff).filter(OnOff.id == 1).one()
    expected_str = (
        "OnOff(id=1, device_id=1, on=True)\n"
        "Device(id=1, mqtt_id=123, online=True, last_seen=None, reboots=0, remote_name=Test On Device - 1, name=Test On Device, device_type_id=1)\n"
        "DeviceType(id=1, name=on_off)\n"
        "[Tag(id=1, name=Main Tag)]"
    )
    assert str(on_device) == expected_str

    off_device = populated_test_db.query(OnOff).filter(OnOff.id == 2).one()
    expected_str = (
        "OnOff(id=2, device_id=2, on=False)\n"
        "Device(id=2, mqtt_id=456, online=True, last_seen=None, reboots=0, remote_name=Test Off Device - 2, name=Test Off Device, device_type_id=1)\n"
        "DeviceType(id=1, name=on_off)\n"
        "Tag=None"
    )
    assert str(off_device) == expected_str
