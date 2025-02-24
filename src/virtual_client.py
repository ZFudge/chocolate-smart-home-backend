import logging

from src.mqtt.client import MQTTClient
from src.plugins.discover_virtual_clients import discover_virtual_clients

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Create a MQTT client for the virtual clients
vcs_mqtt_client = MQTTClient(
    host="mqtt",
    port=1883,
    client_id_prefix="virtual_client_",
    subscription_topics=[],
    message_handler=lambda _: None,
)

# Wait for the MQTT client to connect before loading virtual clients
while not vcs_mqtt_client.is_connected():
    logger.info("Waiting for the initial MQTT client connection...")
    vcs_mqtt_client.connect()

# Discover virtual clients
logger.info("Discovering virtual clients...")
virtual_clients = discover_virtual_clients(vcs_mqtt_client)
