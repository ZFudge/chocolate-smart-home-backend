from typing import Iterable

import src.plugins.device_plugins.neo_pixel.utils as utils


def test_controller_palette_message():
    palette_str = (
        "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,210,220,230,240,250,255"
    )
    palette_msg_seq: Iterable[str] = iter(palette_str.split(","))
    palette_hex_strings = utils.received_controller_palette_value_to_hex_str_tuple(
        palette_msg_seq
    )

    expected_palette_hex_strings = utils.PaletteHexNamedTuple(
        *[
            "#000102",
            "#030405",
            "#060708",
            "#090a0b",
            "#0c0d0e",
            "#0f1011",
            "#121314",
            "#d2dce6",
            "#f0faff",
        ]
    )

    assert expected_palette_hex_strings == palette_hex_strings


def test_default_palette_on_parsing_failure():
    short_palette = "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    payload = iter(short_palette.split(","))

    palette_hex_strings = utils.received_controller_palette_value_to_hex_str_tuple(
        payload
    )

    expected_palette_hex_strings = utils.PaletteHexNamedTuple(*[""] * 9)

    assert expected_palette_hex_strings == palette_hex_strings


def test_hex_list_to_byte_tuple():
    palette = [
        "#00ffff",
        "#0394fc",
        "#0341fc",
        "#0000ff",
        "#5500ff",
        "#7703fc",
        "#ba03fc",
        "#de19ff",
        "#fc03a5",
    ]
    assert utils.hex_list_to_byte_tuple(palette) == utils.PaletteByteNamedTuple(
        0,
        255,
        255,
        3,
        148,
        252,
        3,
        65,
        252,
        0,
        0,
        255,
        85,
        0,
        255,
        119,
        3,
        252,
        186,
        3,
        252,
        222,
        25,
        255,
        252,
        3,
        165,
    )
