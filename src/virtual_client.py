import logging
from time import sleep

from sqlalchemy.exc import IntegrityError

from src.crud import create_tag, put_device_tags
from src.mqtt.client import MQTTClient
from src.plugins.discover_virtual_clients import discover_virtual_clients
from src.schemas import TagBase

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

tag_names = ["vsc tag 1", "vsc tag 2", "vsc tag 3"]
tags = []
for tag_name in tag_names:
    try:
        logger.info(f"Creating virtual client tag: {tag_name}")
        tags.append(create_tag(TagBase(name=tag_name)))
    except IntegrityError as e:
        logger.error(f"Error creating virtual client tag: {e}")

tag_ids = [tag.id for tag in tags]
logger.info(f"{tag_ids=}")

vcs_mqtt_client.request_all_devices_data()

# sleep here is a hacky way of waiting for the virtual clients' published states
# to be received by the backend server and added to the database's Device table.
# This must be completed before adding the tags to the devices, below.
sleep(3)

device_mqtt_ids_and_tag_ids = (
    # Neo pixel
    (900, [1, 2, 3]),
    (901, [1, 2]),
    # On off
    (904, [2, 3]),
    (906, [3]),
    (907, [3]),
)

for device_mqtt_id, tag_ids in device_mqtt_ids_and_tag_ids:
    try:
        logger.info(
            f"Adding tags to virtual client device: {device_mqtt_id=} {tag_ids=}"
        )
        put_device_tags(device_mqtt_id, tag_ids)
    except IntegrityError as e:
        logger.error(f"Error putting virtual client device tags: {e}")
