import logging
from typing import Dict, Iterable, Tuple


logger = logging.getLogger()


class BaseDuplexMessenger:
    def parse_msg(self, raw_msg: str) -> Tuple[Dict, Iterable[str]]:
        """Parse message from remote controller."""
        msg_seq: Iterable[str] = iter(raw_msg.split(","))

        device_data = dict()
        try:
            device_data["mqtt_id"] = next(msg_seq)
            device_data["device_type_name"] = next(msg_seq)
            device_data["remote_name"] = next(msg_seq)
        except StopIteration:
            raise StopIteration(
                f"Not enough comma-separated values in message.payload. payload='{raw_msg}'."
            ) from None

        return device_data, msg_seq

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
