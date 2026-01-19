from contextvars import ContextVar
from typing import Any, Optional

from .client import MQTTClient

mqtt_client_ctx: ContextVar[Optional[MQTTClient]] = ContextVar("mqtt_client_ctx")


def get_mqtt_client(**kwargs: Any) -> MQTTClient:
    try:
        return mqtt_client_ctx.get()
    except LookupError:
        client = MQTTClient(**kwargs)
        mqtt_client_ctx.set(client)
        return client
