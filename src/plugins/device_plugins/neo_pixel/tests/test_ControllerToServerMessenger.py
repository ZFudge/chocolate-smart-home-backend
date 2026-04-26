from ..Schema import NeoPixel


def test_neo_pixel_ControllerToServerMessenger_parse_controller_msg(
    ControllerToServerMessengerWithSuper,
):
    assert (
        ControllerToServerMessengerWithSuper()
        .parse_controller_msg(
            "123,test_device_type_name,test_remote_name,7,2,255,120,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26"
        )
        .plugin.model_dump()
        == NeoPixel(
            on=True,
            twinkle=True,
            all_twinkle_colors_are_current=False,
            transform=True,
            ms=2,
            brightness=255,
            palette=(
                "#000102",
                "#030405",
                "#060708",
                "#090a0b",
                "#0c0d0e",
                "#0f1011",
                "#121314",
                "#151617",
                "#18191a",
            ),
            pir_enabled=False,
            pir_armed=False,
            pir_timeout=120,
        ).model_dump()
    )
