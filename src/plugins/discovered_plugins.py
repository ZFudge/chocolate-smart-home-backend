import importlib
from typing import Dict

import src.plugins.device_plugins
from src.plugins import iter_nametag
from src.plugins.base_device_manager import (
    BaseDeviceManager as DefaultDeviceManager,
)
from src.plugins.base_duplex_messenger import DefaultDuplexMessenger


DISCOVERED_PLUGINS = {}
PLUGIN_ROUTERS = []


def discover_and_import_device_plugin_modules():
    """Iterate through each subdirectory in src/plugins/device_plugins/,
    add its DeviceManager and DuplexMessenger classes and router to a dictionary
    stored in DISCOVERED_PLUGINS dict, using plugin name as a key.
       DISCOVERED_PLUGINS = {
           "plugin_name": {
               "DuplexMessenger": DuplexMessenger,
               "DeviceManager": DeviceManager,
           },
           ...
       }"""
    for _finder, name, _ispkg in iter_nametag(src.plugins.device_plugins):
        device_manager_module_name = f"{name}.device_manager"
        duplex_messenger_module_name = f"{name}.duplex_messenger"
        router_module_name = f"{name}.router"
        db_seeding_module_name = f"{name}.db_seeding"

        device_manager_module = importlib.import_module(device_manager_module_name)
        duplex_messenger_module = importlib.import_module(duplex_messenger_module_name)
        router_module = importlib.import_module(router_module_name)
        try:
            db_seeding_module = importlib.import_module(db_seeding_module_name)
            db_seeding_module.seed_db()
        except ImportError:
            pass

        DeviceManager = device_manager_module.DeviceManager
        DuplexMessenger = duplex_messenger_module.DuplexMessenger

        plugin_router = router_module.plugin_router
        PLUGIN_ROUTERS.append(plugin_router)

        plugin_name = name.split(".").pop()
        DISCOVERED_PLUGINS[plugin_name] = {
            "DuplexMessenger": DuplexMessenger,
            "DeviceManager": DeviceManager,
        }


DEFAULT_PLUGIN = {
    "DuplexMessenger": DefaultDuplexMessenger,
    "DeviceManager": DefaultDeviceManager,
}


def get_plugin_by_device_type(plugin_name: str) -> Dict:
    """Return plugin dictionary, using device_type_name/plugin_name as key."""
    return DISCOVERED_PLUGINS.get(plugin_name.lower(), DEFAULT_PLUGIN)
