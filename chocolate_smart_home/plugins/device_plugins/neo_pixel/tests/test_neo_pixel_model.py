from chocolate_smart_home.plugins.device_plugins.neo_pixel.model import NeoPixel


def test_neo_pixel_model_str(populated_test_db):
    neo_pixel_device_1 = (
        populated_test_db.query(NeoPixel).filter(NeoPixel.id == 1).one()
    )
    expected_str = (
        "NeoPixel(id=1, device_id=1, on=True, twinkle=True, transform=True, ms=5, brightness=255, "
        "palette=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26], "
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
        "palette=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26], "
        "pir_armed=None, pir_timeout_seconds=None)\n"
        "Device(id=2, mqtt_id=456, online=True, reboots=0, remote_name=Test Neo Pixel Device - 2, name=Test Neo Pixel Device Two, device_type_id=1)\n"
        "DeviceType(id=1, name=neo_pixel)\n"
        "Tag=None"
    )
    assert str(neo_pixel_device_2) == expected_str
