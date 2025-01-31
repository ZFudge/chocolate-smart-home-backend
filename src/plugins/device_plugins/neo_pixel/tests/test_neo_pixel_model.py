from src.plugins.device_plugins.neo_pixel.model import NeoPixel


def test_neo_pixel_model_str(populated_test_db):
    neo_pixel_device_1 = (
        populated_test_db.query(NeoPixel).filter(NeoPixel.id == 1).one()
    )
    expected_str = (
        "NeoPixel(id=1, device_id=1, on=True, twinkle=True, transform=True, ms=5, brightness=255, "
        "palette=['#000102', '#030405', '#060708', '#090a0b', '#0c0d0e', '#0f1011', '#121314', '#d2dce6', '#f0faff'], "
        "pir_armed=True, pir_timeout_seconds=172)\n"
        "Device(id=1, mqtt_id=123, online=True, reboots=0, remote_name=Test Neo Pixel Device - 1, name=Test Neo Pixel Device One, device_type_id=1)\n"
        "DeviceType(id=1, name=neo_pixel)\n"
        "[Tag(id=1, name=Main Tag)]"
    )
    assert str(neo_pixel_device_1) == expected_str

    neo_pixel_device_2 = (
        populated_test_db.query(NeoPixel).filter(NeoPixel.id == 2).one()
    )
    expected_str = (
        "NeoPixel(id=2, device_id=2, on=False, twinkle=True, transform=False, ms=55, brightness=123, "
        "palette=['#000102', '#030405', '#060708', '#090a0b', '#0c0d0e', '#0f1011', '#121314', '#d2dce6', '#f0faff'], "
        "pir_armed=None, pir_timeout_seconds=None)\n"
        "Device(id=2, mqtt_id=456, online=True, reboots=0, remote_name=Test Neo Pixel Device - 2, name=Test Neo Pixel Device Two, device_type_id=1)\n"
        "DeviceType(id=1, name=neo_pixel)\n"
        "Tag=None"
    )
    assert str(neo_pixel_device_2) == expected_str
