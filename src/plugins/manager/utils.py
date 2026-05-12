import importlib
import logging
from types import ModuleType

from ..bases import (
    BaseDeviceManager,
    BaseServerToControllerMessenger,
    DefaultControllerToServerMessenger,
)


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
            plugin_name = plugin_path.split(".").pop().split("/").pop()
            kwargs["plugin_name"] = plugin_name
        f(*args, **kwargs)

    return wrapper


def import_plugin_module(plugin_path, name) -> ModuleType | None:
    logger.info(f"Checking for {name} module in {plugin_path}...")
    module_name = f"{plugin_path}.{name}"
    try:
        module: ModuleType = importlib.import_module(module_name)
        return module
    except ModuleNotFoundError:
        logger.info(f"No {module_name} module found.")
    except (ImportError, AttributeError):
        logger.warning(f"Unable to import {module_name}.")
    except Exception as e:
        logger.error(e)


def has_valid_callable(module: ModuleType, name: str) -> bool:
    return hasattr(module, name) and callable(getattr(module, name))
