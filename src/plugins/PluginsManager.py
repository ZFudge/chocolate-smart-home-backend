import importlib
import logging
import os
from typing import Dict

from . import device_plugins
from .BaseDeviceManager import BaseDeviceManager
from .BaseControllerToServerMessenger import (
    BaseControllerToServerMessenger,
    DefaultControllerToServerMessenger,
)
from .BaseServerToControllerMessenger import BaseServerToControllerMessenger
from .utils import iter_nametag

logger = logging.getLogger()


DEFAULT_PLUGIN = {
    "ControllerToServerMessenger": DefaultControllerToServerMessenger,
    "ServerToControllerMessenger": BaseServerToControllerMessenger,
    "DeviceManager": BaseDeviceManager,
}


class PluginsMapper(dict):
    """A dictionary-like mapping object that guarantees key lookups resolve to
    DEFAULT_PLUGIN if the intended plugin cannot be found. This guarantees the
    bare minimum needed for a device to be visible in the application, without
    having to implement any plugin code for it, so long as the client abides by
    the configuration format expected by these defaults.

    I know some folks consider it bad form to subclass dict, *BUT*, because the
    python runtime explicitly provides __missing__ for use in dict subclassing,
    and this subclass only implements __missing__, I can forgive myself <3.
    """

    def __missing__(self, plugin_name):
        logger.warning(
            f"Key lookup for {plugin_name} plugin failed. Falling back to DEFAULT_PLUGIN."
        )
        return DEFAULT_PLUGIN


class PluginDict(dict):
    """A dictionary-like mapping object that tries to retrieve failed key lookups from DEFAULT_PLUGIN.
    Same excuse as above.
    """

    def __missing__(self, key):
        return DEFAULT_PLUGIN.get(key)


def pluginnamefrompath(f):
    def wrapper(*args, **kwargs):
        if "plugin_name" not in kwargs:
            plugin_path = args[1]
            plugin_name = plugin_path.split(".").pop()
            kwargs["plugin_name"] = plugin_name
        f(*args, **kwargs)

    return wrapper


class PluginsManager:
    PLUGINS = PluginsMapper()
    ROUTERS = []

    @classmethod
    def discover_plugins(cls):
        """Iterate through each plugin module subdirectory in src/plugins/device_plugins/,
        checking for the presence of ControllerToServerMessenger, ServerToControllerMessenger,
        and DeviceManager classes and router, providing default values for missing classes.
        Discovered classes are stored in dictionary, mapped into PluginsManager.PLUGINS,
        using the plugin's name as a key.
        PluginsManager.PLUGINS = {
            "plugin_name": {
                "ControllerToServerMessenger": ControllerToServerMessenger,
                "ServerToControllerMessenger": ServerToControllerMessenger,
                "DeviceManager": DeviceManager,
            },
            ...
        }
        Routers are stored in PluginsManager.ROUTERS where they can be later included by the FastAPI app.
        """
        logger.info("Checking for discoverable device plugin modules...")
        for _finder, plugin_path, _ispkg in iter_nametag(device_plugins):
            plugin_name = plugin_path.split(".").pop()
            logger.info(f'Found discoverable device plugin module: "{plugin_name}"')
            cls.add_plugin_object(plugin_path)
            cls.check_device_manager(plugin_path)
            cls.check_controller_to_server_messenger(plugin_path)
            cls.check_server_to_controller_messenger(plugin_path)
            cls.check_router(plugin_path)
            if "PYTEST_VERSION" not in os.environ:
                cls.check_db_seeding(plugin_path)

    @classmethod
    @pluginnamefrompath
    def add_plugin_object(cls, _, *, plugin_name):
        cls.PLUGINS[plugin_name] = PluginDict()

    @classmethod
    @pluginnamefrompath
    def check_device_manager(cls, plugin_path: str, *, plugin_name=None):
        """Check for the presence of a device manager module in the plugin's subdirectory.
        If found, import the module and create a dynamic plugin class that inherits from BaseDeviceManager and the plugin's DeviceManager class.
        If not found, use the default device manager class.
        """
        logger.info(f"Checking for device manager module in {plugin_path}...")
        plugin = cls.PLUGINS[plugin_name]
        DeviceManager = BaseDeviceManager
        try:
            device_manager_module_name = f"{plugin_path}.DeviceManager"
            device_manager_module = importlib.import_module(device_manager_module_name)
            PluginDeviceManager = device_manager_module.DeviceManager
            DeviceManager = type(
                "DeviceManager", (BaseDeviceManager, PluginDeviceManager), {}
            )
        except ModuleNotFoundError:
            logger.info(
                f"No device manager module found for {plugin_path}. Using default device manager."
            )
        except (ImportError, AttributeError):
            logger.warning(
                f"Unable to import device manager from {plugin_path}. Using default device manager."
            )
        except Exception as e:
            logger.warning(e)

        plugin["DeviceManager"] = DeviceManager

    @classmethod
    @pluginnamefrompath
    def check_controller_to_server_messenger(
        cls, plugin_path: str, *, plugin_name=None
    ):
        """Check for the presence of a controller to server messenger module in the plugin's subdirectory.
        If found, import the module and create a dynamic plugin class that inherits from BaseControllerToServerMessenger and the plugin's ControllerToServerMessenger class.
        If not found, use the default controller to server messenger class.
        """
        logger.info(
            f"Checking for controller to server messenger module in {plugin_path}..."
        )
        plugin = cls.PLUGINS[plugin_name]
        ControllerToServerMessenger = DefaultControllerToServerMessenger
        try:
            ctos_messenger_module_name = f"{plugin_path}.ControllerToServerMessenger"
            ctos_messenger_module = importlib.import_module(ctos_messenger_module_name)
            PluginControllerToServerMessenger = (
                ctos_messenger_module.ControllerToServerMessenger
            )
            _BaseControllerToServerMessenger = BaseControllerToServerMessenger
            # if plugin device does not have its own device-specific values to parse,
            # defer to default controller to server messenger to be sure parse_controller_msg returns a device schema
            if not hasattr(PluginControllerToServerMessenger, "parse_controller_msg"):
                _BaseControllerToServerMessenger = DefaultControllerToServerMessenger
            # Creating dynamic plugin classes in place gives access to the super proxy
            ControllerToServerMessenger = type(
                "ControllerToServerMessenger",
                (_BaseControllerToServerMessenger, PluginControllerToServerMessenger),
                {},
            )
        except ModuleNotFoundError:
            logger.info(
                f"No controller to server messenger module found for {plugin_path}. Using default controller to server messenger."
            )
        except (ImportError, AttributeError):
            logger.warning(
                f"Unable to import controller to server messenger from {plugin_path}. Using default controller to server messenger."
            )

        plugin["ControllerToServerMessenger"] = ControllerToServerMessenger

    @classmethod
    @pluginnamefrompath
    def check_server_to_controller_messenger(
        cls, plugin_path: str, *, plugin_name=None
    ):
        """Check for the presence of a server to controller messenger module in the plugin's subdirectory.
        If found, import the module and create a dynamic plugin class that inherits from BaseServerToControllerMessenger and the plugin's ServerToControllerMessenger class.
        If not found, use the default server to controller messenger class.
        """
        logger.info(
            f"Checking for server to controller messenger module in {plugin_path}..."
        )
        plugin_name = plugin_path.split(".").pop()
        plugin = cls.PLUGINS[plugin_name]
        ServerToControllerMessenger = BaseServerToControllerMessenger
        try:
            stoc_messenger_module_name = f"{plugin_path}.ServerToControllerMessenger"
            stoc_messenger_module = importlib.import_module(stoc_messenger_module_name)
            PluginServerToControllerMessenger = (
                stoc_messenger_module.ServerToControllerMessenger
            )
            ServerToControllerMessenger = type(
                "ServerToControllerMessenger",
                (
                    BaseServerToControllerMessenger,
                    PluginServerToControllerMessenger,
                ),
                {},
            )
        except ModuleNotFoundError:
            logger.info(
                f"No server to controller messenger module found for {plugin_path}. Using default server to controller messenger."
            )
        except (ImportError, AttributeError):
            logger.warning(
                f"Unable to import server to controller messenger from {plugin_path}. Using default server to controller messenger."
            )

        plugin["ServerToControllerMessenger"] = ServerToControllerMessenger

    @classmethod
    @pluginnamefrompath
    def check_router(cls, plugin_path: str, *, plugin_name=None):
        """Check for the presence of a router module in the plugin's subdirectory.
        If found, import the module and add the router to the PluginsManager.ROUTERS list.
        If not found, use the default router class.
        """
        logger.info(f"Checking for router module in {plugin_path}...")
        try:
            router_module_name = f"{plugin_path}.router"
            router_module = importlib.import_module(router_module_name)
            plugin_router = router_module.plugin_router
            cls.ROUTERS.append(plugin_router)
        except ModuleNotFoundError:
            logger.info(f"No router module found for {plugin_name}.")
        except (ImportError, AttributeError):
            logger.warning(f"Unable to import router from {plugin_path}.")

    @classmethod
    @pluginnamefrompath
    def check_db_seeding(cls, plugin_path: str, *, plugin_name=None):
        """Check for the presence of a db_seeding module in the plugin's subdirectory.
        If found, import the module and call the seed_db function.
        If not found, log a message.
        """
        logger.info(f"Checking for db_seeding module in {plugin_path}...")
        try:
            db_seeding_module_name = f"{plugin_path}.db_seeding"
            logger.info(
                f"Attempting import of db_seeding module for {db_seeding_module_name}"
            )
            db_seeding_module = importlib.import_module(db_seeding_module_name)
            db_seeding_module.seed_db()
        except ModuleNotFoundError:
            logger.info(f"No db_seeding module found for {plugin_name}.")
        except ImportError:
            logger.warning(f"Unable to import db_seeding from {plugin_path}.")

    @classmethod
    def get_plugin_by_device_type_name(cls, plugin_name: str) -> Dict:
        return cls.PLUGINS[plugin_name.lower()]
