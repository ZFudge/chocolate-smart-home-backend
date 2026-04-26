from .. import utils


def test_hex_to_byte():
    assert utils.hex_to_byte("ff") == 255
    assert utils.hex_to_byte("00") == 0
    assert utils.hex_to_byte("12") == 18


def test_convert_9_hex_to_27_byte_str():
    assert utils.convert_9_hex_to_27_byte_str(
        [
            "#001122",
            "#223344",
            "#445566",
            "#667788",
            "#8899aa",
            "#aabbcc",
            "#ccddee",
            "#eeffff",
            "#148acf",
        ]
    ) == (
        "0,17,34,"
        "34,51,68,"
        "68,85,102,"
        "102,119,136,"
        "136,153,170,"
        "170,187,204,"
        "204,221,238,"
        "238,255,255,"
        "20,138,207"
    )


def test_convert_27_byte_int_to_9_hex_str():
    assert utils.convert_27_byte_int_to_9_hex_str(
        (
            "0",
            "0",
            "0",
            "34",
            "34",
            "34",
            "68",
            "68",
            "68",
            "102",
            "102",
            "102",
            "136",
            "136",
            "136",
            "170",
            "170",
            "170",
            "204",
            "204",
            "204",
            "238",
            "238",
            "238",
            "255",
            "255",
            "255",
        )
    ) == (
        "#000000",
        "#222222",
        "#444444",
        "#666666",
        "#888888",
        "#aaaaaa",
        "#cccccc",
        "#eeeeee",
        "#ffffff",
    )


def test_received_controller_palette_value_to_hex_str_tuple():
    raw_msg = (
        "0,17,34,"
        "34,51,68,"
        "68,85,102,"
        "102,119,136,"
        "136,153,170,"
        "170,187,204,"
        "204,221,238,"
        "238,255,255,"
        "20,138,207"
    )
    msg = iter(raw_msg.split(","))
    utils.received_controller_palette_value_to_hex_str_tuple(msg)


def test_StopIteration_empty_response_received_controller_palette_value_to_hex_str_tuple():
    raw_msg = (
        "0,17,34,"
        "34,51,68,"
        "68,85,102,"
        "102,119,136,"
        "136,153,170,"
        "170,187,204,"
        "204,221,238,"
        "238,255,255,"
        "20,138"
    )
    msg = iter(raw_msg.split(","))
    assert utils.received_controller_palette_value_to_hex_str_tuple(msg) == (
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
    )


def test_ValueError_empty_response_received_controller_palette_value_to_hex_str_tuple():
    raw_msg = (
        "0,17,34,"
        "34,51,68,"
        "68,85,102,"
        "102,119,136,"
        "136,153,170,"
        "170,187,204,"
        "204,221,238,"
        "238,255,255,"
        "20,138,cabbage"
    )
    msg = iter(raw_msg.split(","))
    assert utils.received_controller_palette_value_to_hex_str_tuple(msg) == (
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
    )
