import logging
import os

from paho.mqtt.client import CallbackAPIVersion, Client


logger = logging.getLogger(os.environ.get("LOGGER", "mqtt"))


def get_configured_mqtt_client() -> Client:
    """Returns configured MQTT client"""
    client_prefix = os.environ.get("MQTT_CLIENT_ID_PREFIX", "")
    client_id_main = os.environ.get("MQTT_CLIENT_ID", "CSM-FASTAPI-SERVER")
    if client_prefix:
        client_id = "-".join([client_prefix, client_id_main])
    else:
        client_id = client_id_main
    logger.info(f'Creating MQTT client with client id "{client_id}')
    return Client(CallbackAPIVersion.VERSION2, client_id=client_id)
