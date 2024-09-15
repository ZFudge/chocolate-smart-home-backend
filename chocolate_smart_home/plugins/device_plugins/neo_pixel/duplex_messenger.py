from types import MappingProxyType
from typing import Dict

from chocolate_smart_home.plugins.base_duplex_messenger import BaseDuplexMessenger


class NeoPixelDuplexMessenger(BaseDuplexMessenger):
    """Adapts data between app and MQTT."""

    INCOMING_LOOKUP = MappingProxyType({
        "0": False,
        "1": True,
    })

    OUTGOING_LOOKUP = MappingProxyType({
        False: "0",
        True: "1",
    })

    def parse_msg(self, incoming_msg: str) -> Dict:
        """Parse incoming message from controller."""
        device_data, msg_seq = super().parse_msg(incoming_msg)

        neo_pixel_value: str = next(msg_seq)
        device_data["on"] = NeoPixelDuplexMessenger.INCOMING_LOOKUP[neo_pixel_value]

        return device_data

    def compose_msg(self, on: bool) -> str:
        """Compose outgoing message to be published to controller."""
        return NeoPixelDuplexMessenger.OUTGOING_LOOKUP[on]


# Alias messenger for use in ..discovered_plugins.DISCOVERED_PLUGINS["neo_pixel"] dict.
DuplexMessenger = NeoPixelDuplexMessenger
