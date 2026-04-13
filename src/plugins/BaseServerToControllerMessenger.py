import logging
from typing import Callable, Iterable

from src.pubsub import topics
from src.schemas import WebsocketMessage as WebsocketMessageSchema


logger = logging.getLogger()


class BaseServerToControllerMessenger:
    @staticmethod
    def compose_controller_msg(msg: str, *args, **kwargs):
        """Implemented at the plugin level.
        Defined here to allow compatibility with controllers that accept messages without formatting or validation
        """
        return msg

    @staticmethod
    def get_mqtt_topics(ws_msg: WebsocketMessageSchema) -> Iterable[str]:
        """Accepts data from websocket and returns list of topics to broadcast this data to."""
        format_topic_by_mqtt_id: Callable = (
            topics.get_format_topic_by_mqtt_id_using_device_type_name(
                ws_msg.device_type_name
            )
        )
        return map(format_topic_by_mqtt_id, ws_msg.get_mqtt_ids())

    @staticmethod
    def _compose_param(key: str, val: str) -> str:
        return f"&{key}={val}"
