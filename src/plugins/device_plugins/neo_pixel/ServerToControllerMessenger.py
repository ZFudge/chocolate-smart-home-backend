from typing import Any

from . import utils


def kvp_param(key: str, value: Any) -> str:
    return f"{key}={value};"


def key_and_bool_value(data: dict, key: str) -> str:
    return kvp_param(key, int(bool(data[key]))) if data.get(key) is not None else ""


def key_and_value(data: dict, key: str) -> str:
    if data.get(key) is None:
        return ""
    value = data[key]
    try:
        value = int(value)
    except ValueError:
        pass
    if isinstance(value, int):
        value = max(0, value)
        value = min(255, value)
    return kvp_param(key, value)


class ServerToControllerMessenger:
    @staticmethod
    def compose_controller_msg(data: dict) -> str | None:
        """Compose outgoing message to be published through MQTT."""
        msg = ""

        msg += key_and_bool_value(data, "on")
        msg += key_and_bool_value(data, "twinkle")
        msg += key_and_bool_value(data, "transform")

        msg += key_and_value(data, "ms")
        msg += key_and_value(data, "brightness")

        msg += key_and_bool_value(data, "armed")
        msg += key_and_value(data, "timeout")

        if data.get("palette") is not None:
            # Palette is a list of 9 hex strings. Convert to a commas-separated list of 27 bytes
            # and embed in outgoing controller message
            palette_27_byte_str = utils.convert_9_hex_to_27_byte_str(data["palette"])
            msg += "palette={};".format(palette_27_byte_str)

        return msg
