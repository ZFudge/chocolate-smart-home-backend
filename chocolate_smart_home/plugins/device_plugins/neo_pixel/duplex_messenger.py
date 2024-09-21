from types import MappingProxyType
from typing import Dict

from pydantic import ValidationError

from chocolate_smart_home.plugins.base_duplex_messenger import BaseDuplexMessenger
from .schemas import NeoPixelOptions, NeoPixelValues


class NeoPixelDuplexMessenger(BaseDuplexMessenger):
    """Adapts data between app and MQTT."""

    OUTGOING_LOOKUP = MappingProxyType({
        False: "0",
        True: "1",
    })

    def parse_msg(self, incoming_msg: str) -> Dict:
        """Parse incoming message from controller."""
        device_data, msg_seq = super().parse_msg(incoming_msg)

        bools_byte = int(next(msg_seq))

        device_data["on"] = bools_byte & 1
        device_data["twinkle"] = bools_byte >> 1 & 1
        device_data["transform"] = bools_byte >> 2 & 1

        device_data["ms"] = int(next(msg_seq))
        device_data["brightness"] = int(next(msg_seq))

        device_data["palette"] = tuple(map(int, [next(msg_seq) for _ in range(27)]))

        try:
            NeoPixelValues(
                on=device_data["on"],
                twinkle=device_data["twinkle"],
                transform=device_data["transform"],
                ms=device_data["ms"],
                brightness=device_data["brightness"],
                palette=device_data["palette"],
            )
        except ValidationError:
            raise

        return device_data

    def compose_msg(self, data: NeoPixelOptions) -> str:
        """Compose outgoing message to be published to controller."""
        msg = ""

        if hasattr(data, "on") and data.on is not None:
            msg += "on={};".format(NeoPixelDuplexMessenger.OUTGOING_LOOKUP[data.on])

        if hasattr(data, "twinkle") and data.twinkle is not None:
            msg += "twinkle={};".format(NeoPixelDuplexMessenger.OUTGOING_LOOKUP[data.twinkle])

        if hasattr(data, "transform") and data.transform is not None:
            msg += "transform={};".format(NeoPixelDuplexMessenger.OUTGOING_LOOKUP[data.transform])

        if hasattr(data, "ms") and data.ms is not None:
            msg += "ms={};".format(data.ms)

        if hasattr(data, "brightness") and data.brightness is not None:
            msg += "brightness={};".format(data.brightness)

        if hasattr(data, "palette") and data.palette is not None:
            palette_str = ",".join(map(str, data.palette))
            msg += "palette={};".format(palette_str)

        return msg


# Alias messenger for use in ..discovered_plugins.DISCOVERED_PLUGINS["neo_pixel"] dict.
DuplexMessenger = NeoPixelDuplexMessenger
