import logging
from typing import Callable, Dict, Iterable, Tuple

from chocolate_smart_home.mqtt import topics
import chocolate_smart_home.schemas as schemas


logger = logging.getLogger()


class BaseDuplexMessenger:
    @staticmethod
    def parse_msg(raw_msg: str) -> Tuple[schemas.DeviceReceived, Iterable[str]]:
        """Parse message from remote controller."""
        msg_seq: Iterable[str] = iter(raw_msg.split(","))

        try:
            mqtt_id: str = next(msg_seq)
            device_type_name: str = next(msg_seq)
            remote_name: str = next(msg_seq)
            device = schemas.DeviceReceived(
                mqtt_id=mqtt_id,
                device_type_name=device_type_name,
                remote_name=remote_name,
            )
        except StopIteration:
            raise StopIteration(
                f"Not enough comma-separated values in message.payload. payload='{raw_msg}'."
            ) from None

        return device, msg_seq

    @staticmethod
    def serialize(data: schemas.DeviceReceived) -> dict:
        """Serialize device data for broadcast through webocket."""
        return data.model_dump()

    @staticmethod
    def compose_msg():
        """Implemented at the plugin level"""
        pass

    @staticmethod
    def get_topics(*, device_type_name: str, data: dict) -> Iterable[str]:
        """Accepts data from websocket and returns list of topics to broadcast this data to.
        Still returns a list of topics, even if the data contains only one id."""

        if "mqtt_ids" not in data and "mqtt_id" not in data:
            raise ValueError(
                "Incoming data must contain 'mqtt_ids' (iterable) or 'mqtt_id' (int or str) key."
            )

        # Every plugin inherits the ability to broadcast data to multiple devices,
        # but only those receiving a payload that implements the "ids" key can use it.
        # Payloads intended for single devices use the "id" key.
        if "mqtt_id" in data:
            mqtt_ids = data["mqtt_id"]
        else:
            mqtt_ids = data["mqtt_ids"]

        format_topic_by_device_id: Callable = topics.get_format_topic_by_device_id(
            device_type_name
        )
        return map(format_topic_by_device_id, mqtt_ids)

    @staticmethod
    def _compose_param(key: str, val: str) -> str:
        return f"&{key}={val}"


class DefaultDuplexMessenger(BaseDuplexMessenger):
    def parse_msg(self, raw_msg: str) -> Dict:
        """Parse message from remote controller, omitting empty list iterator."""
        device_data, _ = super().parse_msg(raw_msg)

        return device_data
