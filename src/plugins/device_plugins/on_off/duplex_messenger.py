from types import MappingProxyType
from typing import Dict, List
import logging

from src.plugins.base_duplex_messenger import (
    BaseDuplexMessenger,
)
from src.schemas.device import DeviceFrontend
from src.schemas.tag import Tag
from .schemas import OnOffDeviceFrontend, OnOffDeviceReceived


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
            return OnOffDeviceReceived(on=False, device=device)

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

    def serialize_db_objects(self, data: OnOffDeviceFrontend | List[OnOffDeviceFrontend]) -> dict:
        """Serialize neo pixel data for broadcast through webocket."""
        if not isinstance(data, (list, tuple, set)):
            data = [data]
        serialized_data = []

        for db_on_off_device in data:
            device = DeviceFrontend(
                mqtt_id=db_on_off_device.device.mqtt_id,
                device_type_name="on_off",
                remote_name=db_on_off_device.device.remote_name,
                name=db_on_off_device.device.name,
                last_seen=str(db_on_off_device.device.last_seen),
            )
            if db_on_off_device.device.tags:
                device.tags = [Tag(id=tag.id, name=tag.name) for tag in db_on_off_device.device.tags]

            on_off_data = OnOffDeviceFrontend(
                device=device,
                on=db_on_off_device.on,
            )
            serialized_data.append(self.serialize(on_off_data))

        return serialized_data


# Alias messenger for use in ..discovered_plugins.DISCOVERED_PLUGINS["on_off"] dict.
DuplexMessenger = OnOffDuplexMessenger
