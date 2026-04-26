import re

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
        "armed": True,
        "timeout": 10,
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
        "armed": False,
        "timeout": 35,
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
        "armed": False,
        "timeout": 17,
    },
]


def compose_outgoing_msg(vc_state: dict) -> str:
    """Mocks the controller state expected by the CSM server"""
    bools_byte = (
        int(vc_state["on"])
        | int(vc_state["twinkle"]) << 1
        | int(vc_state["transform"]) << 2
        | int(vc_state["all_twinkle_colors_are_current"]) << 3
        | int(vc_state["pir"]) << 4
        | int(vc_state["armed"]) << 5
    )

    palette = vc_state["palette"]
    if len(palette) == 9:
        palette = convert_9_hex_to_27_byte_str(palette)

    msg_values = [
        # Add configs
        vc_state["mqtt_id"],
        vc_state["device_type_name"],
        vc_state["name"],
        # Add state
        bools_byte,
        vc_state["ms"],
        vc_state["brightness"],
        vc_state["timeout"],
        palette,
    ]

    msg_values = map(str, msg_values)

    return ",".join(msg_values)


def parse_incoming_payload(payload: str) -> tuple[str, str]:
    key, value = re.split("=|;", payload)[:2]
    return key, value
