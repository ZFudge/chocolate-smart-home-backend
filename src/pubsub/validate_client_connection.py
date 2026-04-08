import logging

from src.dependencies import mqtt_client_session 

logger = logging.getLogger("mqtt")


def validate_client_connection(f):
    def wrapper(*args, **kwargs):
        mqtt_client = mqtt_client_session.get()
        if not mqtt_client.is_connected():
            logger.error("MQTT client is not connected to the MQTT broker")
            return
        f(*args, mqtt_client=mqtt_client, **kwargs)

    return wrapper
