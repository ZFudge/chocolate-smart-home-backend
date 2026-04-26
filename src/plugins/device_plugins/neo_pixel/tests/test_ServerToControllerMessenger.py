from ..ServerToControllerMessenger import ServerToControllerMessenger


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_empty():
    assert ServerToControllerMessenger().compose_controller_msg({}) == ""


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_multiple():
    assert (
        ServerToControllerMessenger().compose_controller_msg(
            {
                "on": True,
                "twinkle": True,
                "transform": True,
                "ms": 100,
                "brightness": 50,
            }
        )
        == "on=1;twinkle=1;transform=1;ms=100;brightness=50;"
    )


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_on():
    assert (
        ServerToControllerMessenger().compose_controller_msg({"on": False}) == "on=0;"
    )


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_twinkle():
    assert (
        ServerToControllerMessenger().compose_controller_msg({"twinkle": True})
        == "twinkle=1;"
    )


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_transform():
    assert (
        ServerToControllerMessenger().compose_controller_msg({"transform": True})
        == "transform=1;"
    )


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_ms():
    assert ServerToControllerMessenger().compose_controller_msg({"ms": 43}) == "ms=43;"


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_max_limit_ms():
    assert (
        ServerToControllerMessenger().compose_controller_msg({"ms": 543}) == "ms=255;"
    )


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_str_min_limit_ms():
    assert ServerToControllerMessenger().compose_controller_msg({"ms": "-9"}) == "ms=0;"


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_min_limit_ms():
    assert ServerToControllerMessenger().compose_controller_msg({"ms": -321}) == "ms=0;"


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_brightness():
    assert (
        ServerToControllerMessenger().compose_controller_msg({"brightness": 43})
        == "brightness=43;"
    )


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_max_limit_brightness():
    assert (
        ServerToControllerMessenger().compose_controller_msg({"brightness": 543})
        == "brightness=255;"
    )


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_str_min_limit_brightness():
    assert (
        ServerToControllerMessenger().compose_controller_msg({"brightness": "-9"})
        == "brightness=0;"
    )


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_min_limit_brightness():
    assert (
        ServerToControllerMessenger().compose_controller_msg({"brightness": -321})
        == "brightness=0;"
    )


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_armed():
    assert (
        ServerToControllerMessenger().compose_controller_msg({"armed": False})
        == "armed=0;"
    )


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_timeout():
    assert (
        ServerToControllerMessenger().compose_controller_msg({"timeout": 5})
        == "timeout=5;"
    )


def test_neo_pixel_ServerToControllerMessenger_compose_controller_msg_palette():
    assert (
        ServerToControllerMessenger().compose_controller_msg(
            {
                "palette": [
                    "#ff0099",
                    "#0099ff",
                    "#99ff00",
                    "#123456",
                    "#789abc",
                    "#def012",
                    "#decaff",
                    "#987654",
                    "#3210fe",
                ]
            }
        )
        == "palette=255,0,153,0,153,255,153,255,0,18,52,86,120,154,188,222,240,18,222,202,255,152,118,84,50,16,254;"
    )
