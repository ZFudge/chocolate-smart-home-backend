import logging
import re
from random import random
from time import sleep
from types import ModuleType
from typing import Callable, Dict

from src import SingletonMeta
from src.plugins import device_plugins, utils
from src.pubsub import topics
from src.pubsub.comm_funcs import subscribe, publish
from . import defaults, helper_funcs

logger = logging.getLogger(__name__)


class DiscoverVirtualClients(metaclass=SingletonMeta):
    mqtt_id = 900
    virtual_clients = {}
    compose_funcs_mapping = {}

    def __init__(self) -> None:
        logger.info("Discovering virtual clients...")
        self.discover_virtual_clients()
        logger.info(
            f"Virtual clients discovered: {list(DiscoverVirtualClients.virtual_clients.keys())}"
        )
        if DiscoverVirtualClients.virtual_clients:
            DiscoverVirtualClients.subscribe_clients()

    def discover_virtual_clients(self) -> None:
        """Discover all virtual clients in the src/plugins/device_plugins/<device_type_name>/virtual_client_seeds.py files."""
        for _finder, plugin_name, _ispkg in utils.iter_nametag(device_plugins):
            logger.info(f"Checking for virtual clients in {plugin_name} plugin")
            vcs_module_name = f"{plugin_name}.virtual_client_seeds"
            vcs_module = helper_funcs.import_vcs_module(vcs_module_name)
            if not helper_funcs.validate_virtual_client_module(vcs_module):
                logger.warning(
                    f"None or invalid virtual client module: {vcs_module_name}"
                )
                continue
            short_name = plugin_name.split(".")[-1]
            self.register_virtual_clients_by_plugin(vcs_module, short_name)

    @classmethod
    def subscribe_clients(cls) -> None:
        def publish_all_vc_states(_client, userdata, message):
            # Publish the states of all devices
            for vc_state in cls.virtual_clients.values():
                translate_func = cls.compose_funcs_mapping[vc_state["device_type_name"]]
                virtual_state_string = translate_func(vc_state)
                publish(
                    topic=topics.RECEIVE_DEVICE_DATA,
                    message=virtual_state_string,
                )

        subscribe(topic=topics.REQUEST_DEVICE_DATA_ALL, handler=publish_all_vc_states)

    def register_virtual_clients_by_plugin(
        self, vcs_module: ModuleType, short_name: str
    ) -> None:
        if hasattr(vcs_module, "compose_state_as_msg"):
            # default translation function handles common configurations
            def trans_func(msg: str):
                return ",".join(
                    [
                        defaults.default_compose_state_as_msg(msg),
                        vcs_module.compose_state_as_msg,
                    ]
                )

        else:
            trans_func = defaults.default_compose_state_as_msg
        DiscoverVirtualClients.compose_funcs_mapping[short_name] = trans_func

        if hasattr(vcs_module, "parse_payload"):
            parser = vcs_module.parse_payload
        else:
            parser = defaults.parse_payload
        data_received_handler = DiscoverVirtualClients.get_data_received_handler(parser)

        format_topic_by_mqtt_id = (
            topics.get_format_topic_by_mqtt_id_using_device_type_name(short_name)
        )
        for seed_state in vcs_module.seeds:
            self.load_vc_state(seed_state, short_name)
            self.subscribe_vc(format_topic_by_mqtt_id, data_received_handler)
            logger.info(
                f"Added {short_name} virtual client {DiscoverVirtualClients.mqtt_id}"
            )
            DiscoverVirtualClients.mqtt_id += 1

    @classmethod
    def load_vc_state(cls, seed_state: Dict, short_name: str) -> None:
        seed_state |= dict(mqtt_id=cls.mqtt_id, device_type_name=short_name)
        cls.virtual_clients[cls.mqtt_id] = seed_state

    @classmethod
    def subscribe_vc(
        cls, format_topic_by_mqtt_id: Callable, data_received_handler: Callable
    ) -> None:
        topic = format_topic_by_mqtt_id(cls.mqtt_id)
        subscribe(topic=topic, handler=data_received_handler)

    @classmethod
    def get_data_received_handler(cls, parse_payload: Callable) -> Callable:
        def data_received_handler(_client, _userdata, message):
            logger.info(f"Received message: {message.topic} {message.payload.decode()}")

            topic = message.topic
            mqtt_id = re.sub(r"[^\d]", "", topic)
            device_type_name = re.sub(r"[^A-Za-z|_]", "", topic)

            try:
                vc: Dict | None = cls.virtual_clients.get(int(mqtt_id))
            except ValueError as e:
                logger.error("Invalid mqtt_id: %s: %s", mqtt_id, e)
                return
            if vc is None:
                logger.error(f"Virtual client not found for mqtt_id: {mqtt_id}")
                return

            payload = message.payload.decode()
            try:
                key, value = parse_payload(payload)
            except ValueError:
                logger.error("Invalid payload: %s" % payload)
                return

            try:
                vc[key] = value
            except Exception as e:
                logger.error("Error setting key-value pair: %s=%s: %s", key, value, e)
                return

            translate_func = cls.compose_funcs_mapping.get(device_type_name)
            outgoing_msg = translate_func(vc)
            # reflect virtual client state changes to the CSM server
            logger.info(f"{device_type_name} virtual client message: {outgoing_msg}")
            try:
                # Simulate the delay observed across different controllers
                sleep(random() * 2 + 0.5)
                publish(topic=topics.RECEIVE_DEVICE_DATA, message=outgoing_msg)
            except Exception as e:
                logger.debug(f"Error publishing message: {e}")

        return data_received_handler
