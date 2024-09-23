import logging
from typing import Dict, Iterable, Tuple

from chocolate_smart_home.schemas import DeviceReceived


logger = logging.getLogger()


class BaseDuplexMessenger:
    def parse_msg(self, raw_msg: str) -> Tuple[DeviceReceived, Iterable[str]]:
        """Parse message from remote controller."""
        msg_seq: Iterable[str] = iter(raw_msg.split(","))

        try:
            mqtt_id = next(msg_seq)
            device_type_name = next(msg_seq)
            remote_name = next(msg_seq)
            device = DeviceReceived(
                mqtt_id=mqtt_id,
                device_type_name=device_type_name,
                remote_name=remote_name
            )
        except StopIteration:
            raise StopIteration(
                f"Not enough comma-separated values in message.payload. payload='{raw_msg}'."
            ) from None

        return device, msg_seq

    def compose_msg():
        """Implemented at the plugin level"""
        pass

    @staticmethod
    def _compose_param(key: str, val: str) -> str:
        return f"&{key}={val}"


class DefaultDuplexMessenger(BaseDuplexMessenger):
    def parse_msg(self, raw_msg: str) -> Dict:
        """Parse message from remote controller, omitting empty list iterator."""
        device_data, _ = super().parse_msg(raw_msg)

        return device_data
