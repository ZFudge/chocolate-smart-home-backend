import importlib
import logging
import os
from types import ModuleType

from src import dependencies


logger = logging.getLogger()


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


def inject_dependencies(module: ModuleType) -> bool:
    dependency_names = (
        "asyncio_event_loop",
        "db_session",
        "mqtt_client_session",
        "redis_session",
    )
    for dn in dependency_names:
        if dn in dir(module):
            setattr(module, dn, getattr(dependencies, dn).get())


def has_scheduling_module(plugin_path: str) -> bool:
    return os.path.exists(
        os.path.join("/backend/", plugin_path.replace(".", "/")) + "/scheduling.py"
    )
