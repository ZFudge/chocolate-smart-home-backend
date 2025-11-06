from random import random
from time import sleep
from typing import Callable, Dict, List
import importlib
import logging
import re

from src.mqtt.client import MQTTClient
from src.mqtt.topics import (
    get_format_topic_by_device_id,
    RECEIVE_DEVICE_DATA,
    REQUEST_DEVICE_DATA_ALL,
)
from src.plugins import iter_nametag
import src.plugins.device_plugins


logger = logging.getLogger(__name__)


def get_data_received_handler(
    *,
    mqtt_client: MQTTClient,
    virtual_clients: Dict,
    translate_vc_dict_to_mqtt_msg: Callable,
    parse_payload: Callable,
) -> Callable:
    def data_received_handler(_client, _userdata, message):
        logger.info(f"Received message: {message.topic} {message.payload.decode()}")
        # Simulate the delay observed across different controllers
        sleep(random() * 2 + 0.5)

        topic = message.topic
        mqtt_id = re.sub(r"[^\d]", "", topic)
        if not mqtt_id.isdigit():
            logger.error(f"Invalid mqtt_id: {mqtt_id}")
            return

        mqtt_id = int(mqtt_id)
        if mqtt_id not in virtual_clients:
            logger.error(f"mqtt_id: {mqtt_id} not in virtual_clients")
            return

        vc: Dict = virtual_clients.get(mqtt_id)
        device_type_name = re.sub(r"[^A-Za-z|_]", "", topic)
        msg = f"{mqtt_id},{device_type_name}"
        logger.info(f"{device_type_name} id: {mqtt_id} virtual_client: {vc}")

        payload = message.payload.decode()
        try:
            key, value = parse_payload(payload)
        except ValueError:
            logger.error("Invalid payload: %s" % payload)
            return None

        if key is not None and value is not None:
            old_value = vc.get(key)
            logger.info(f'{vc=}', f'{payload=}', f'{key=}', f'{value=}', f'{old_value=}')
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
        # reflect virtual client state changes to the CSM server
        logger.info(f"{device_type_name} virtual client message: {msg}")

        try:
            mqtt_client.publish(topic=RECEIVE_DEVICE_DATA, message=msg)
        except Exception as e:
            logger.debug(f"Error publishing message: {e}")

    return data_received_handler


def discover_virtual_clients(client: MQTTClient) -> List[str]:
    """Discover all virtual clients in the system."""
    mqtt_id = 900
    virtual_clients = dict()
    trans_funcs = dict()

    for _finder, name, _ispkg in iter_nametag(src.plugins.device_plugins):
        logger.info(f"plugin name: {name}")
        vcs_module_name = f"{name}.virtual_client_seeds"
        short_name = name.split(".")[-1]

        try:
            vcs_module = importlib.import_module(vcs_module_name)
            logger.info(f"Imported {vcs_module_name}")
        except ImportError:
            logger.warning(
                "No %s.virtual_client_seeds module found for %s", (short_name, name)
            )
            continue

        try:
            seeds = vcs_module.seeds
            trans_funcs[short_name] = vcs_module.translate_vc_dict_to_mqtt_msg
            parse_payload = vcs_module.parse_payload
        except AttributeError:
            logger.warning("No seeds found for %s", short_name)
            continue

        format_topic_by_device_id = get_format_topic_by_device_id(short_name)

        data_received_handler = get_data_received_handler(
            mqtt_client=client,
            virtual_clients=virtual_clients,
            translate_vc_dict_to_mqtt_msg=trans_funcs[short_name],
            parse_payload=parse_payload,
        )

        for seed in seeds:
            seed |= dict(mqtt_id=mqtt_id, device_type_name=short_name)
            virtual_clients[mqtt_id] = seed
            logger.info(f"Added virtual {short_name} client: {seed}")

            topic = format_topic_by_device_id(seed["mqtt_id"])
            logger.info(f"Subscribed to {topic}")

            client.subscribe(topic=topic, handler=data_received_handler)
            mqtt_id += 1

    def publish_states(_client, userdata, message):
        # Publish the states of all devices
        for mqtt_id, vc_mem_state in virtual_clients.items():
            translate_func = trans_funcs[vc_mem_state["device_type_name"]]
            virtual_state_string = translate_func(vc_mem_state)
            client.publish(topic=RECEIVE_DEVICE_DATA, message=virtual_state_string)

    logger.info(f"Virtual clients discovered: {virtual_clients}")
    # Subscribe to all devices data request
    client.subscribe(topic=REQUEST_DEVICE_DATA_ALL, handler=publish_states)

    return virtual_clients
