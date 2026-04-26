import logging
import os
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

logger = logging.getLogger("vcs")


class VirtualClientsManager(metaclass=SingletonMeta):
    mqtt_id = 900
    virtual_clients = {}
    outgoing_msg_composer_funcs = {}

    def discover(self):
        logger.info("Discovering virtual clients...")
        self.discover_virtual_clients()
        logger.info(
            f"Virtual clients discovered: {list(VirtualClientsManager.virtual_clients.keys())}"
        )
        if VirtualClientsManager.virtual_clients:
            VirtualClientsManager.subscribe_vc_manager()

    def discover_virtual_clients(self) -> None:
        """Discover all virtual clients in the src/plugins/device_plugins/<device_type_name>/virtual_client_seeds.py files."""
        for _finder, plugin_name, _ispkg in utils.iter_nametag(device_plugins):
            logger.info(f"Checking for {plugin_name} virtual clients...")
            vcs_module_name = f"{plugin_name}.virtual_client_seeds"
            vcs_module = helper_funcs.import_vcs_module(vcs_module_name)
            if not helper_funcs.validate_virtual_client_module(vcs_module):
                continue
            device_type_name = plugin_name.split(".")[-1]
            self.register_virtual_clients_by_plugin(vcs_module, device_type_name)

    @classmethod
    def subscribe_vc_manager(cls) -> None:
        def publish_all_vc_states(_client, userdata, message):
            # Publish the states of all devices
            for vc_state in cls.virtual_clients.values():
                composer_func = cls.outgoing_msg_composer_funcs[
                    vc_state["device_type_name"]
                ]
                virtual_state_string = composer_func(vc_state)
                publish(
                    topic=topics.RECEIVE_DEVICE_DATA,
                    message=virtual_state_string,
                )

        subscribe(topic=topics.REQUEST_DEVICE_DATA_ALL, handler=publish_all_vc_states)

    def register_virtual_clients_by_plugin(
        self, vcs_module: ModuleType, device_type_name: str
    ) -> None:
        """Extract and map virtual client seeds into VirtualClientsManager.virtual_clients; assigning and mapping each with an mqtt_id.

        Map each plugin's compose_outgoing_msg to VirtualClientsManager.outgoing_msg_composer_funcs;
        *Provides a default_compose_outgoing_msg if the plugin is stateless.

        Subscribe vc to individual device topic, using the module's parse_incoming_payload function as message handler;
        **Provides a default_parse_incoming_payload if the plugin is stateless and/or does not accept device-specific commands.

        *A device can parse idempotent input with its parse_incoming_payload,
        but not have any modified state that requires its own compose_outgoing_msg implementation.

        **A device could be a sensor that publishes sensor data with its compose_outgoing_msg output,
        while not accepting incoming commands that require it to have its own parse_incoming_payload implementation.
        """
        if hasattr(vcs_module, "compose_outgoing_msg"):
            # device is stateful
            # the default composer function still handles the common configurations; mqtt id, device type name, and remote name
            # while the module's compose_outgoing_msg handles virtual client state
            def compose_outgoing_msg(msg: str):
                root_msg = defaults.default_compose_outgoing_msg(msg)
                state_msg = vcs_module.compose_outgoing_msg(msg)
                msg = ",".join(
                    [
                        root_msg,
                        state_msg,
                    ]
                )
                while msg[-1] == ",":
                    # if plugin's composer returns an empty string, remove trailing comma
                    msg = msg[:-1]
                return msg

        else:
            # device is stateless. only sends its configuration; mqtt id, device type name, and remote name
            compose_outgoing_msg = defaults.default_compose_outgoing_msg
        VirtualClientsManager.outgoing_msg_composer_funcs[device_type_name] = (
            compose_outgoing_msg
        )

        if hasattr(vcs_module, "parse_incoming_payload"):
            # device accepts input
            parse_incoming_payload = vcs_module.parse_incoming_payload
        else:
            # device does not accept input
            parse_incoming_payload = defaults.default_parse_incoming_payload
        data_received_handler = VirtualClientsManager.get_data_received_handler(
            parse_incoming_payload
        )

        format_topic_by_mqtt_id = (
            topics.get_format_topic_by_mqtt_id_using_device_type_name(device_type_name)
        )
        for seed_state in vcs_module.seeds:
            self.init_vc_state_from_seed(seed_state, device_type_name)
            self.subscribe_vc(format_topic_by_mqtt_id, data_received_handler)
            # Must wait for both state load and subscribe before incrementing mqtt_id
            VirtualClientsManager.mqtt_id += 1
            logger.info(
                f"Added {device_type_name} virtual client {VirtualClientsManager.mqtt_id}"
            )

    @classmethod
    def init_vc_state_from_seed(cls, seed_state: Dict, device_type_name: str) -> None:
        vc_state = seed_state | dict(
            mqtt_id=cls.mqtt_id, device_type_name=device_type_name
        )
        cls.virtual_clients[cls.mqtt_id] = vc_state

    @classmethod
    def subscribe_vc(
        cls, format_topic_by_mqtt_id: Callable, data_received_handler: Callable
    ) -> None:
        topic = format_topic_by_mqtt_id(cls.mqtt_id)
        subscribe(topic=topic, handler=data_received_handler)

    @classmethod
    def get_data_received_handler(cls, parse_incoming_payload: Callable) -> Callable:
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
                key, value = parse_incoming_payload(payload)
            except ValueError:
                logger.error("Invalid payload: %s" % payload)
                return

            vc[key] = value

            composer_func = cls.outgoing_msg_composer_funcs.get(device_type_name)
            outgoing_msg = composer_func(vc)
            # reflect virtual client state changes to the CSM server
            logger.info(f"{device_type_name} virtual client message: {outgoing_msg}")
            try:
                if "PYTEST_CURRENT_TEST" not in os.environ:
                    # Simulate the delay observed across different controllers
                    sleep(random() * 2 + 0.5)
                publish(topic=topics.RECEIVE_DEVICE_DATA, message=outgoing_msg)
            except Exception as e:
                logger.debug(f"Error publishing message: {e}")

        return data_received_handler
