from types import MappingProxyType
from typing import Dict
import logging

from src.plugins.base_duplex_messenger import (
    BaseDuplexMessenger,
)
from .schemas import OnOffDeviceReceived


logger = logging.getLogger(__name__)


class OnOffDuplexMessenger(BaseDuplexMessenger):
    """Adapts data between app and MQTT."""

    INCOMING_LOOKUP = MappingProxyType(
        {
            "0": False,
            "1": True,
        }
    )

    OUTGOING_LOOKUP = MappingProxyType(
        {
            False: "0",
            True: "1",
        }
    )

    def parse_msg(self, incoming_msg: str) -> Dict:
        """Parse incoming message from controller."""
        device, msg_seq = super().parse_msg(incoming_msg)

        try:    
            on_off_value: str = next(msg_seq)
        except StopIteration:
            logger.error(
                "Not enough comma-separated values in message.payload. payload='%s'."
                % incoming_msg
            )
            logger.info("Returning default on=False for device %s", device)
            return OnOffDeviceReceived(
                on=False, device=device
            )

        return OnOffDeviceReceived(
            on=OnOffDuplexMessenger.INCOMING_LOOKUP[on_off_value], device=device
        )

    def compose_msg(self, on: bool | dict) -> str:
        """Compose outgoing message to be published to controller."""
        if isinstance(on, dict):
            return OnOffDuplexMessenger.OUTGOING_LOOKUP[on["on"]]
        return OnOffDuplexMessenger.OUTGOING_LOOKUP[on]

    def serialize(self, data: OnOffDeviceReceived) -> dict:
        """Serialize neo pixel data for broadcast through webocket."""
        device_dict = super().serialize(data.device)
        on_off_dict = data.model_dump()
        on_off_dict.update(device_dict)
        del on_off_dict["device"]
        return on_off_dict


# Alias messenger for use in ..discovered_plugins.DISCOVERED_PLUGINS["on_off"] dict.
DuplexMessenger = OnOffDuplexMessenger
