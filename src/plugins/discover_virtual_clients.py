from time import sleep
from typing import Callable, Dict, List
import importlib
import logging
import re

from src.mqtt.client import MQTTClient
from src.mqtt.topics import get_format_topic_by_device_id, RECEIVE_DEVICE_DATA, REQUEST_DEVICE_DATA_ALL
from src.plugins import iter_nametag
import src.plugins.device_plugins


logger = logging.getLogger(__name__)


def get_echo_handler(*, mqtt_client: MQTTClient, virtual_clients: Dict, translate_vc_dict_to_mqtt_msg: Callable) -> Callable:
    def echo_handler(_client, _userdata, message):
        logger.info(f"Received message: {message.topic} {message.payload.decode()}")
        sleep(1)

        topic = message.topic
        mqtt_id = re.sub(r'[^\d]', '', topic)
        if not mqtt_id.isdigit():
            logger.error(f"Invalid mqtt_id: {mqtt_id}")
            return

        mqtt_id = int(mqtt_id)
        if mqtt_id not in virtual_clients:
            logger.error(f"mqtt_id: {mqtt_id} not in virtual_clients")
            return

        vc: Dict = virtual_clients.get(mqtt_id)
        device_type_name = re.sub(r'[^A-Za-z]', '', topic)
        msg = f"{mqtt_id},{device_type_name}"
        logger.info(f"{device_type_name} id: {mqtt_id} virtual_client: {vc}")

        payload = message.payload.decode()
        try:
            key, value = re.split('=|;', payload)[:2]
        except ValueError:
            logger.error("Invalid payload: %s" % payload)
            return

        old_value = vc.get(key)
        if old_value is None:
            vc[key] = value
        elif isinstance(old_value, bool):
            try:
                vc[key] = int(value) == 1
            except ValueError:
                vc[key] = value == "True"
        elif isinstance(old_value, int):
            try:
                vc[key] = int(value)
            except ValueError:
                vc[key] = value
        elif isinstance(old_value, float):
            vc[key] = float(value)
        else:
            vc[key] = value

        msg = translate_vc_dict_to_mqtt_msg(vc)
        logger.info(f"{device_type_name} virtual client message: {msg}")

        try:
            mqtt_client.publish(topic=RECEIVE_DEVICE_DATA, message=msg)
        except Exception as e:
            logger.error(f"Error publishing message: {e}")

    return echo_handler

def discover_virtual_clients(client: MQTTClient) -> List[str]:
    """Discover all virtual clients in the system."""
    mqtt_id = 900
    virtual_clients = dict()

    for _finder, name, _ispkg in iter_nametag(src.plugins.device_plugins):
        vcs_module_name = f"{name}.virtual_client_seeds"
        short_name = name.split(".")[-1]

        try:
            vcs_module = importlib.import_module(vcs_module_name)
        except ImportError:
            logger.warning("No %s.virtual_client_seeds module found for %s", (short_name, name))
            continue

        try:
            seeds = vcs_module.seeds
            translate_vc_dict_to_mqtt_msg = vcs_module.translate_vc_dict_to_mqtt_msg
        except AttributeError as e:
            logger.warning("No seeds found for %s", short_name)
            continue

        format_topic_by_device_id = get_format_topic_by_device_id(short_name)

        echo_handler = get_echo_handler(
            mqtt_client=client,
            virtual_clients=virtual_clients,
            translate_vc_dict_to_mqtt_msg=translate_vc_dict_to_mqtt_msg
        )

        for seed in seeds:
            seed |= dict(mqtt_id=mqtt_id, device_type_name=short_name)
            virtual_clients[mqtt_id] = seed
            logger.info(seed)

            topic = format_topic_by_device_id(seed["mqtt_id"])
            logger.info(topic)

            client.subscribe(topic=topic, handler=echo_handler)
            mqtt_id += 1

    def publish_states(_client, userdata, message):
        logger.info(f"publish_states message: {message.topic} {message.payload.decode()}")
        # Publish the states of all devices
        for mqtt_id, vc_dict in virtual_clients.items():
            virtual_state_string = translate_vc_dict_to_mqtt_msg(vc_dict)
            client.publish(topic=RECEIVE_DEVICE_DATA, message=virtual_state_string)

    # Subscribe to all devices data request
    client.subscribe(topic=REQUEST_DEVICE_DATA_ALL, handler=publish_states)
