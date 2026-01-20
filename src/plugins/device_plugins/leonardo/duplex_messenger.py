import logging

from src.plugins.base_duplex_messenger import (
    BaseDuplexMessenger,
)
from src.schemas import DeviceReceived
from src.models import Device as models_Device


logger = logging.getLogger(__name__)


class LeonardoDuplexMessenger(BaseDuplexMessenger):
    """Adapts data between app and MQTT."""

    OUTGOING_MESSAGES = frozenset[str](["move", "lock", "unlock", "talon"])

    def compose_msg(self, msg_data: dict | str) -> str:
        """Compose outgoing message to be published to controller."""
        msg = ""
        if isinstance(msg_data, str):
            msg = msg_data
        elif isinstance(msg_data, dict):
            msg = msg_data.get("command", "")
        if msg not in LeonardoDuplexMessenger.OUTGOING_MESSAGES:
            raise ValueError(f"Invalid message: {msg}")
        return msg

    def parse_msg(self, incoming_msg: str) -> DeviceReceived:
        """Parse incoming message from controller."""
        device, _ = super().parse_msg(incoming_msg)
        return device

    def serialize_db_obj(self, db_leonardo_device: models_Device) -> dict:
        """Serialize device data for broadcast through webocket."""
        fe_device = self.get_device_frontend(db_leonardo_device, "leonardo")
        return super().serialize(fe_device)


# Alias messenger for use in ..discovered_plugins.DISCOVERED_PLUGINS["leonardo"] dict.
DuplexMessenger = LeonardoDuplexMessenger
