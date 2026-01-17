from src.plugins.device_plugins.neo_pixel.model import NeoPixel


def test_neo_pixel_model_str(populated_test_db):
    neo_pixel_device_1 = (
        populated_test_db.query(NeoPixel).filter(NeoPixel.id == 1).one()
    )
    expected_str = (
        "NeoPixel(id=1, device_id=1, on=True, twinkle=True, all_twinkle_colors_are_current=None, scheduled_palette_rotation=True, transform=True, ms=5, brightness=255, "
        "palette=['#000102', '#030405', '#060708', '#090a0b', '#0c0d0e', '#0f1011', '#121314', '#d2dce6', '#f0faff'], "
        "armed=True, timeout=172)\n"
        "Device(id=1, mqtt_id=123, last_seen=2025-01-02 00:00:00, last_update_sent=2025-01-01 00:00:00, reboots=0, remote_name=Test Neo Pixel Device - 1, name=Test Neo Pixel Device One, device_type_id=1)\n"
        "DeviceType(id=1, name=neo_pixel)\n"
        "[Tag(id=1, name=NeoPixel Tag)]"
    )
    assert str(neo_pixel_device_1) == expected_str

    neo_pixel_device_2 = (
        populated_test_db.query(NeoPixel).filter(NeoPixel.id == 2).one()
    )
    expected_str = (
        "NeoPixel(id=2, device_id=2, on=False, twinkle=True, all_twinkle_colors_are_current=None, scheduled_palette_rotation=None, transform=False, ms=55, brightness=123, "
        "palette=['#000102', '#030405', '#060708', '#090a0b', '#0c0d0e', '#0f1011', '#121314', '#d2dce6', '#f0faff'], "
        "armed=None, timeout=None)\n"
        "Device(id=2, mqtt_id=456, last_seen=2025-01-02 00:00:00, last_update_sent=2025-01-01 00:00:00, reboots=0, remote_name=Test Neo Pixel Device - 2, name=Test Neo Pixel Device Two, device_type_id=1)\n"
        "DeviceType(id=1, name=neo_pixel)\n"
        "Tag=None"
    )
    assert str(neo_pixel_device_2) == expected_str
