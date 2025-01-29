from contextvars import ContextVar
import os
from typing import Optional

from .client import DEFAULT_MQTT_HOST, MQTTClient

mqtt_client_ctx: ContextVar[Optional[MQTTClient]] = ContextVar("mqtt_client_ctx")


def get_mqtt_client() -> MQTTClient:
    try:
        return mqtt_client_ctx.get()
    except LookupError:
        client = MQTTClient(host=os.environ.get("MQTT_HOST", DEFAULT_MQTT_HOST))
        mqtt_client_ctx.set(client)
        return client
