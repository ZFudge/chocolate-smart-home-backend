from types import MappingProxyType
from typing import Dict

from chocolate_smart_home.plugins.base_duplex_messenger import (
    BaseDuplexMessenger,
)
from .schemas import OnOffDeviceReceived


class OnOffDuplexMessenger(BaseDuplexMessenger):
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
        device, msg_seq = super().parse_msg(incoming_msg)

        on_off_value: str = next(msg_seq)
        on_off_device_data = OnOffDeviceReceived(
            on=OnOffDuplexMessenger.INCOMING_LOOKUP[on_off_value],
            device=device
        )

        return on_off_device_data

    def compose_msg(self, on: bool) -> str:
        """Compose outgoing message to be published to controller."""
        return OnOffDuplexMessenger.OUTGOING_LOOKUP[on]


# Alias messenger for use in ..discovered_plugins.DISCOVERED_PLUGINS["on_off"] dict.
DuplexMessenger = OnOffDuplexMessenger
