import logging
from time import sleep

from sqlalchemy.exc import IntegrityError, NoResultFound

from src import crud, schemas
from src.dependencies import mqtt_client_session
from src.pubsub import connect_to_mqtt_broker, request_all_devices_data
from src.plugins.virtual_clients.discover_virtual_clients import DiscoverVirtualClients

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Create a MQTT client for the virtual clients
mqtt_client = mqtt_client_session.get()

# Wait for the MQTT client to connect before loading virtual clients
while not mqtt_client.is_connected():
    logger.info("Waiting for the initial MQTT client connection...")
    connect_to_mqtt_broker()
    sleep(5)


discovered_vcs = DiscoverVirtualClients()
sleep(3)

request_all_devices_data()

tag_names = list(map(lambda x: f"vsc tag {x}", range(1, 4)))
db_tags = [crud.create_tag(tag_name=tn) for tn in tag_names]

# sleep here is a hacky way of waiting for the virtual clients' published states
# to be received by the backend server and added to the database's Device table.
# This must be completed before adding the tags to the devices, below.
sleep(5)

device_mqtt_ids_and_tag_ids = (
    (900, [1, 2, 3]),
    (901, [1, 2]),
    # (904, [2, 3]),
    # (906, [3]),
    # (907, [3]),
)

logger.info(f"Discovered virtual clients: {discovered_vcs.virtual_clients}")

logger.info("Patching virtual client tags")
for device_mqtt_id, tag_ids in device_mqtt_ids_and_tag_ids:
    if not device_mqtt_id in discovered_vcs.virtual_clients:
        logger.warning("vcs mqtt id %s was not found in discovered clients", 900)
        continue
    logger.info(f"Adding tags to virtual client device: {device_mqtt_id=} {tag_ids=}")
    try:
        device = schemas.DevicePatch(
            mqtt_id=device_mqtt_id,
            tags=tag_ids,
        )
        crud.patch_device(device)
    except (IntegrityError, NoResultFound) as e:
        logger.error("Error putting virtual client device tags: %s", e)
