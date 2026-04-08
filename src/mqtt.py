import logging
import os

from paho.mqtt.client import Client, CallbackAPIVersion


logger = logging.getLogger("mqtt")


def get_configured_mqtt_client() -> Client:
    """Returns configured MQTT client"""
    client_id_prefix = os.environ.get("MQTT_CLIENT_ID", "CSM-FASTAPI-SERVER")
    client_suffix = os.environ.get("MQTT_CLIENT_ID_SUFFIX", "")
    client_id = "_".join([client_id_prefix, client_suffix])
    logger.info(f'Creating MQTT client with client id "{client_id}')
    return Client(CallbackAPIVersion.VERSION2, client_id=client_id)
