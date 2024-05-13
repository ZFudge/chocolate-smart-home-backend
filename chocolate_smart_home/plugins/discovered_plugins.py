import importlib
from typing import Dict

import chocolate_smart_home.plugins.device_plugins
from chocolate_smart_home.plugins import iter_namespace
from chocolate_smart_home.plugins.base_device_manager import BaseDeviceManager as DefaultDeviceManager
from chocolate_smart_home.plugins.base_duplex_messenger import DefaultDuplexMessenger


DISCOVERED_PLUGINS = {}

# Iterate through each subdirectory in chocolate_smart_home/plugins/device_plugins/,
# add its DeviceManager and DuplexMessenger classes to a dictionary, and add the
# dictionary to DISCOVERED_PLUGINS, using the plugin directory name as a key.
#    DISCOVERED_PLUGINS = {
#        "plugin_name": {
#            "DuplexMessenger": DuplexMessenger,
#            "DeviceManager": DeviceManager,
#        }
#    }
for _finder, name, _ispkg in iter_namespace(chocolate_smart_home.plugins.device_plugins):
    device_manager_module_name = f"{name}.device_manager"
    duplex_messenger_module_name = f"{name}.duplex_messenger"

    device_manager_module = importlib.import_module(device_manager_module_name)
    duplex_messenger_module = importlib.import_module(duplex_messenger_module_name)

    DeviceManager = device_manager_module.DeviceManager
    DuplexMessenger = duplex_messenger_module.DuplexMessenger

    plugin_name = name.split('.').pop()
    DISCOVERED_PLUGINS[plugin_name] = {
        "DuplexMessenger": DuplexMessenger,
        "DeviceManager": DeviceManager,
    }

DEFAULT_PLUGIN = {
    "DuplexMessenger": DefaultDuplexMessenger,
    "DeviceManager": DefaultDeviceManager,
}

def get_device_plugin_by_device_type(plugin_name: str) -> Dict:
    """Return plugin dictionary, using device_type_name/plugin_name as key."""
    return DISCOVERED_PLUGINS.get(plugin_name.lower(), DEFAULT_PLUGIN)
