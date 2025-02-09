import logging

from src.mqtt.client import MQTTClient
from src.plugins.discover_virtual_clients import discover_virtual_clients

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


client = MQTTClient(
    host="mqtt",
    port=1883,
    client_id_prefix="virtual_client_",
    subscription_topics=[],
    message_handler=lambda _: None,
)

client.connect()

virtual_clients = discover_virtual_clients(client)
