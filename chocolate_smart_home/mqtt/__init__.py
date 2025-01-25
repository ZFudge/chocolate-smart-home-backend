from contextvars import ContextVar
import os
from typing import Optional
import multiprocessing

from .client import DEFAULT_MQTT_HOST, MQTTClient

mqtt_client_ctx: ContextVar[Optional[MQTTClient]] = ContextVar("mqtt_client_ctx")

def get_mqtt_client() -> MQTTClient:
    try:
        return mqtt_client_ctx.get()
    except LookupError:
        # Only initialize in the worker process
        if multiprocessing.current_process().name == 'MainProcess':
            # Skip initialization in parent process
            return None
        client = MQTTClient(host=os.environ.get("MQTT_HOST", DEFAULT_MQTT_HOST))
        mqtt_client_ctx.set(client)
        return client
