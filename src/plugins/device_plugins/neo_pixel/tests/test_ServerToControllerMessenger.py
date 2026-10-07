def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_on_converts_bool_to_str(
    ServerToControllerMessengerWithSuper,
):
    assert (
        ServerToControllerMessengerWithSuper().compose_controller_msg(
            {
                "name": "on",
                "value": False,
                "mqtt_id": 123,
                "device_type_name": "",
            }
        )
        == "on=0;"
    )


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_on_uses_str(
    ServerToControllerMessengerWithSuper,
):
    assert (
        ServerToControllerMessengerWithSuper().compose_controller_msg(
            {
                "name": "on",
                "value": "0",
                "mqtt_id": 123,
                "device_type_name": "",
            }
        )
        == "on=0;"
    )


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_twinkle(
    ServerToControllerMessengerWithSuper,
):
    assert (
        ServerToControllerMessengerWithSuper().compose_controller_msg(
            {
                "name": "twinkle",
                "value": True,
                "mqtt_id": 123,
                "device_type_name": "",
            }
        )
        == "twinkle=1;"
    )


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_transform(
    ServerToControllerMessengerWithSuper,
):
    assert (
        ServerToControllerMessengerWithSuper().compose_controller_msg(
            {
                "name": "transform",
                "value": True,
                "mqtt_id": 123,
                "device_type_name": "",
            }
        )
        == "transform=1;"
    )


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_ms(
    ServerToControllerMessengerWithSuper,
):
    assert (
        ServerToControllerMessengerWithSuper().compose_controller_msg(
            {
                "name": "ms",
                "value": 43,
                "mqtt_id": 123,
                "device_type_name": "",
            }
        )
        == "ms=43;"
    )


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_max_limit_ms(
    ServerToControllerMessengerWithSuper,
):
    assert (
        ServerToControllerMessengerWithSuper().compose_controller_msg(
            {
                "name": "ms",
                "value": 567,
                "mqtt_id": 123,
                "device_type_name": "",
            }
        )
        == "ms=255;"
    )


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_str_min_limit_ms(
    ServerToControllerMessengerWithSuper,
):
    assert (
        ServerToControllerMessengerWithSuper().compose_controller_msg(
            {
                "name": "ms",
                "value": -9,
                "mqtt_id": 123,
                "device_type_name": "",
            }
        )
        == "ms=0;"
    )


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_min_limit_ms(
    ServerToControllerMessengerWithSuper,
):
    assert (
        ServerToControllerMessengerWithSuper().compose_controller_msg(
            {
                "name": "ms",
                "value": -321,
                "mqtt_id": 123,
                "device_type_name": "",
            }
        )
        == "ms=0;"
    )


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_brightness(
    ServerToControllerMessengerWithSuper,
):
    assert (
        ServerToControllerMessengerWithSuper().compose_controller_msg(
            {
                "name": "brightness",
                "value": 43,
                "mqtt_id": 123,
                "device_type_name": "",
            }
        )
        == "brightness=43;"
    )


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_max_limit_brightness(
    ServerToControllerMessengerWithSuper,
):
    assert (
        ServerToControllerMessengerWithSuper().compose_controller_msg(
            {
                "name": "brightness",
                "value": 543,
                "mqtt_id": 123,
                "device_type_name": "",
            }
        )
        == "brightness=255;"
    )


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_str_min_limit_brightness(
    ServerToControllerMessengerWithSuper,
):
    assert (
        ServerToControllerMessengerWithSuper().compose_controller_msg(
            {
                "name": "brightness",
                "value": "-9",
                "mqtt_id": 123,
                "device_type_name": "",
            }
        )
        == "brightness=0;"
    )


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_min_limit_brightness(
    ServerToControllerMessengerWithSuper,
):
    assert (
        ServerToControllerMessengerWithSuper().compose_controller_msg(
            {
                "name": "brightness",
                "value": -321,
                "mqtt_id": 123,
                "device_type_name": "",
            }
        )
        == "brightness=0;"
    )


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_armed(
    ServerToControllerMessengerWithSuper,
):
    assert (
        ServerToControllerMessengerWithSuper().compose_controller_msg(
            {
                "name": "pir_armed",
                "value": False,
                "mqtt_id": 123,
                "device_type_name": "",
            }
        )
        == "pir_armed=0;"
    )


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_timeout(
    ServerToControllerMessengerWithSuper,
):
    assert (
        ServerToControllerMessengerWithSuper().compose_controller_msg(
            {
                "name": "pir_timeout",
                "value": 5,
                "mqtt_id": 123,
                "device_type_name": "",
            }
        )
        == "pir_timeout=5;"
    )


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_palette(
    ServerToControllerMessengerWithSuper,
):
    assert (
        ServerToControllerMessengerWithSuper().compose_controller_msg(
            {
                "name": "palette",
                "value": [
                    "#ff0099",
                    "#0099ff",
                    "#99ff00",
                    "#123456",
                    "#789abc",
                    "#def012",
                    "#decaff",
                    "#987654",
                    "#3210fe",
                ],
                "mqtt_id": 123,
                "device_type_name": "",
            }
        )
        == "palette=255,0,153,0,153,255,153,255,0,18,52,86,120,154,188,222,240,18,222,202,255,152,118,84,50,16,254;"
    )
