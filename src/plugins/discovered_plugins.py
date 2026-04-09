import importlib
import logging
import pkgutil
import os
from typing import Dict

from . import device_plugins
from .base_device_manager import BaseDeviceManager
from .base_duplex_messenger import (
    BaseDuplexMessenger,
    DefaultDuplexMessenger,
)

logger = logging.getLogger()


def iter_nametag(ns_pkg):
    # Specifying the second argument (prefix) to iter_modules makes the
    # returned name an absolute name instead of a relative one. This allows
    # import_module to work without having to do additional modification to
    # the name.
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


DISCOVERED_PLUGINS = {}
PLUGIN_ROUTERS = []
DEFAULT_PLUGIN = {
    "DuplexMessenger": DefaultDuplexMessenger,
    "DeviceManager": BaseDeviceManager,
}


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
    logger.info("Discovering and importing device plugin modules...")

    for _finder, name, _ispkg in iter_nametag(device_plugins):
        logger.info(f"importing device plugin module: {name}")

        plugin_name = name.split(".").pop()
        plugin_dict = {}
        DISCOVERED_PLUGINS[plugin_name] = plugin_dict

        # Device Manager
        try:
            device_manager_module_name = f"{name}.device_manager"
            device_manager_module = importlib.import_module(device_manager_module_name)
            DeviceManager = device_manager_module.DeviceManager
            PluginDeviceManager = type(
                "DeviceManager", (BaseDeviceManager, DeviceManager), {}
            )
            plugin_dict["DeviceManager"] = PluginDeviceManager
        except ModuleNotFoundError:
            plugin_dict["DeviceManager"] = BaseDeviceManager
        except (ImportError, AttributeError):
            logger.warning(
                "Unable to import device manager from %s for %s plugin",
                device_manager_module_name,
                name,
            )

        # Duplex Messenger
        try:
            duplex_messenger_module_name = f"{name}.duplex_messenger"
            duplex_messenger_module = importlib.import_module(
                duplex_messenger_module_name
            )
            DuplexMessenger = duplex_messenger_module.DuplexMessenger

            # Creating dynamic plugin classes in place gives access to the super proxy
            PluginDuplexMessenger = type(
                "DuplexMessenger", (BaseDuplexMessenger, DuplexMessenger), {}
            )
            plugin_dict["DuplexMessenger"] = PluginDuplexMessenger
        except ModuleNotFoundError:
            plugin_dict["DuplexMessenger"] = DefaultDuplexMessenger
        except (ImportError, AttributeError):
            logger.warning(
                "Unable to import duplex messenger from %s for %s plugin",
                duplex_messenger_module_name,
                name,
            )

        # Device Router
        try:
            router_module_name = f"{name}.router"
            router_module = importlib.import_module(router_module_name)
            plugin_router = router_module.plugin_router
            PLUGIN_ROUTERS.append(plugin_router)
        except ModuleNotFoundError:
            pass
        except (ImportError, AttributeError):
            logger.warning(
                "Unable to import router from %s for %s plugin",
                router_module_name,
                name,
            )

        # Don't seed db in pytest tests
        if "PYTEST_VERSION" in os.environ:
            continue

        try:
            db_seeding_module_name = f"{name}.db_seeding"
            logger.info(
                f"Attempting import of db_seeding module for {name} at {db_seeding_module_name}"
            )
            db_seeding_module = importlib.import_module(db_seeding_module_name)
            db_seeding_module.seed_db()
        except ModuleNotFoundError:
            pass
        except ImportError:
            logger.warning(
                "Unable to import db_seeding from %s for %s plugin",
                db_seeding_module_name,
                name,
            )


def get_plugin_by_device_type_name(plugin_name: str) -> Dict:
    """Return plugin dictionary, using device_type_name/plugin_name as key."""
    return DISCOVERED_PLUGINS.get(plugin_name.lower(), DEFAULT_PLUGIN)
