from contextvars import ContextVar
import os

from .client import DEFAULT_MQTT_HOST, MQTTClient

mqtt_client_ctx: ContextVar[MQTTClient] = ContextVar(
    "mqtt_client_ctx",
    default=MQTTClient(host=os.environ.get("MQTT_HOST", DEFAULT_MQTT_HOST)),
)
