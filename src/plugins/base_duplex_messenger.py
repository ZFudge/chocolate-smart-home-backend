import logging
from typing import Callable, Iterable, Tuple

from src.schemas import (
    device_mod_obj_to_frontend_schema as to_frontend_schema,
    DeviceFrontend as DeviceFrontendSchema,
    DeviceReceived as DeviceReceivedSchema,
    WebsocketMessage as WebsocketMessageSchema,
)
from src.models import Device as models_Device
from src.mqtt.topics import get_format_topic_by_mqtt_id


logger = logging.getLogger()


class IncomingMessenger:
    @staticmethod
    def parse_msg(raw_msg: str) -> Tuple[DeviceReceivedSchema, Iterable[str]]:
        """Parse message from remote controller."""
        msg_seq: Iterable[str] = iter(raw_msg.split(","))
        try:
            mqtt_id: str = next(msg_seq)
            device_type_name: str = next(msg_seq)
            remote_name: str = next(msg_seq)
            device = DeviceReceivedSchema(
                mqtt_id=mqtt_id,
                device_type_name=device_type_name,
                remote_name=remote_name,
                name=remote_name,
            )
            return device, msg_seq
        except StopIteration:
            raise StopIteration(
                f"Not enough comma-separated values in message.payload. payload='{raw_msg}'."
            ) from None

    @staticmethod
    def compose_msg(msg: str, *args, **kwargs):
        """Implemented at the plugin level"""
        return msg

    @staticmethod
    def get_topics(ws_msg: WebsocketMessageSchema) -> Iterable[str]:
        """Accepts data from websocket and returns list of topics to broadcast this data to."""
        format_topic_by_mqtt_id: Callable = get_format_topic_by_mqtt_id(
            ws_msg.device_type_name
        )
        return map(format_topic_by_mqtt_id, ws_msg.get_mqtt_ids())

    @staticmethod
    def _compose_param(key: str, val: str) -> str:
        return f"&{key}={val}"


class OutgoingMessenger:
    @staticmethod
    def get_device_frontend(db_device: models_Device) -> DeviceFrontendSchema:
        return to_frontend_schema(db_device)


class BaseDuplexMessenger(IncomingMessenger, OutgoingMessenger):
    pass


class DefaultDuplexMessenger(BaseDuplexMessenger):
    def parse_msg(self, raw_msg: str) -> DeviceReceivedSchema:
        """Parse message from remote controller, omitting empty list iterator."""
        device: DeviceReceivedSchema = super().parse_msg(raw_msg)[0]
        return device
