# seed data for virtual clients, to simulate neo pixel controllers during development

from src.plugins.device_plugins.neo_pixel.utils import convert_9_hex_to_27_byte_str


seeds = [
    {
        "name": "Virtual Neo Pixel 1",
        "device_type_name": "neo_pixel",
        "on": True,
        "brightness": 255,
        "ms": 7,
        "twinkle": True,
        "all_twinkle_colors_are_current": True,
        "transform": True,
        "palette": [
            "#FF0000",
            "#00FF00",
            "#0000FF",
            "#FFFF00",
            "#00FFFF",
            "#FF00FF",
            "#FFA500",
            "#800080",
            "#008000",
        ],
        "pir": True,
        "pir_armed": True,
        "pir_timeout": 10,
    },
    {
        "name": "Virtual Neo Pixel 2",
        "device_type_name": "neo_pixel",
        "on": False,
        "brightness": 255,
        "ms": 11,
        "twinkle": False,
        "all_twinkle_colors_are_current": False,
        "transform": True,
        "palette": [
            "#0000FF",
            "#00FF00",
            "#00FFFF",
            "#800080",
            "#008000",
            "#FFA500",
            "#FF0000",
            "#0000FF",
            "#00FF00",
        ],
        "pir": True,
        "pir_armed": False,
        "pir_timeout": 35,
    },
    {
        "name": "Virtual Neo Pixel 3",
        "device_type_name": "neo_pixel",
        "on": True,
        "brightness": 255,
        "ms": 3,
        "twinkle": True,
        "all_twinkle_colors_are_current": False,
        "transform": False,
        "palette": [
            "#0000FF",
            "#00FF00",
            "#00FFFF",
            "#800080",
            "#008000",
            "#FFA500",
            "#FF0000",
            "#0000FF",
            "#00FF00",
        ],
        "pir": True,
        "pir_armed": False,
        "pir_timeout": 17,
    },
]


def translate_vc_dict_to_mqtt_msg(seed: dict) -> str:
    """Mocks the controller state expected by the CSM server"""
    bools_byte = (
        int(seed["on"])                                      |
        int(seed["twinkle"])                            << 1 |
        int(seed["transform"])                          << 2 |
        int(seed["all_twinkle_colors_are_current"])     << 3 |
        int(seed["pir"])                                << 4 |
        int(seed["pir_armed"])                          << 5
    )

    msg_values = [
        # Add configs
        seed["mqtt_id"],
        seed["device_type_name"],
        seed["name"],
        # Add state
        bools_byte,
        seed["ms"],
        seed["brightness"],
        seed["pir_timeout"],
        convert_9_hex_to_27_byte_str(seed["palette"]),
    ]

    msg_values = map(str, msg_values)

    return ",".join(msg_values)
