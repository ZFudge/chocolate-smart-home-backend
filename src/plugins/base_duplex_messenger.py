import logging
from typing import Callable, Dict, Iterable, Tuple

from src.mqtt import topics
import src.schemas as schemas


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
    def serialize(data: schemas.DeviceFrontend) -> dict:
        """Serialize device data for broadcast through webocket."""
        data = data.model_dump()
        data["online"] = True
        return data

    @staticmethod
    def compose_msg(msg: str, *args, **kwargs):
        """Implemented at the plugin level"""
        return msg

    @staticmethod
    def get_topics(ws_msg: schemas.WebsocketMessage) -> Iterable[str]:
        """Accepts data from websocket and returns list of topics to broadcast this data to.
        Still returns a list of topics, even if the data contains only one id."""
        format_topic_by_device_id: Callable = topics.get_format_topic_by_device_id(
            ws_msg.device_type_name
        )
        return map(format_topic_by_device_id, ws_msg.get_mqtt_ids())

    @staticmethod
    def _compose_param(key: str, val: str) -> str:
        return f"&{key}={val}"


class DefaultDuplexMessenger(BaseDuplexMessenger):
    def parse_msg(self, raw_msg: str) -> Dict:
        """Parse message from remote controller, omitting empty list iterator."""
        device_data, _ = super().parse_msg(raw_msg)

        return device_data
