import importlib
import logging

from sqlalchemy import Column, ForeignKey, Integer

from src import dependencies, utils
from src.database import Base, engine
from . import device_plugins
from .BaseControllerToServerMessenger import (
    BaseControllerToServerMessenger,
    DefaultControllerToServerMessenger,
)
from .BaseDeviceManager import BaseDeviceManager
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
            plugin_name = plugin_path.split(".").pop().split("/").pop()
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
            logger.info(
                f'Found discoverable device plugin "{plugin_name}" : {plugin_path}'
            )
            try:
                cls.load_plugin_from_path(plugin_path)
            except Exception as e:
                logger.error(e)

    @classmethod
    def load_plugin_from_path(cls, plugin_path: str):
        cls.map_new_plugin(plugin_path)
        cls.check_device_manager(plugin_path)
        cls.check_controller_to_server_messenger(plugin_path)
        cls.check_server_to_controller_messenger(plugin_path)
        cls.check_model(plugin_path)
        cls.check_extra_models(plugin_path)
        cls.check_router(plugin_path)
        cls.check_db_seeding(plugin_path)

    @classmethod
    @pluginnamefrompath
    def map_new_plugin(cls, _, *, plugin_name):
        cls.PLUGINS[plugin_name] = PluginDict()

    @classmethod
    @pluginnamefrompath
    def check_device_manager(cls, plugin_path: str, *, plugin_name=None):
        """Check for the presence of a DeviceManager module in the plugin's subdirectory.
        If found, import the module and create a dynamic plugin class that inherits from BaseDeviceManager and the plugin's DeviceManager class.
        If not found, use the BaseDeviceManager class.
        """
        logger.info(f"Checking for DeviceManager module in {plugin_path}...")
        plugin = cls.PLUGINS[plugin_name]
        DeviceManager = BaseDeviceManager
        try:
            device_manager_module_name = f"{plugin_path}.DeviceManager"
            device_manager_module = importlib.import_module(device_manager_module_name)
            PluginDeviceManager = device_manager_module.DeviceManager
            DeviceManager = type(
                "DeviceManager",
                (
                    PluginDeviceManager,
                    BaseDeviceManager,
                ),
                {},
            )
        except ModuleNotFoundError:
            logger.info(
                f"No DeviceManager module found for {plugin_path}. Using BaseDeviceManager."
            )
        except (ImportError, AttributeError) as e:
            logger.warning(
                f"Unable to import DeviceManager from {plugin_path}. Using BaseDeviceManager."
            )
            logger.warning(e)
        except Exception as e:
            logger.error(e)

        plugin["DeviceManager"] = DeviceManager

    @classmethod
    @pluginnamefrompath
    def check_controller_to_server_messenger(
        cls, plugin_path: str, *, plugin_name=None
    ):
        """Check for the presence of a ControllerToServerMessenger module in the plugin's subdirectory.
        If found, import the module and create a dynamic plugin class that inherits from DefaultControllerToServerMessenger and the plugin's ControllerToServerMessenger class.
        If not found, use the DefaultControllerToServerMessenger class.
        """
        logger.info(
            f"Checking for ControllerToServerMessenger module in {plugin_path}..."
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
            # defer to DefaultControllerToServerMessenger to be sure parse_controller_msg returns a device schema
            if not hasattr(PluginControllerToServerMessenger, "parse_controller_msg"):
                _BaseControllerToServerMessenger = DefaultControllerToServerMessenger
            # Creating dynamic plugin classes in place gives access to the super proxy
            ControllerToServerMessenger = type(
                "ControllerToServerMessenger",
                (
                    PluginControllerToServerMessenger,
                    _BaseControllerToServerMessenger,
                ),
                {},
            )
        except ModuleNotFoundError:
            logger.info(
                f"No ControllerToServerMessenger module found for {plugin_path}. Using DefaultControllerToServerMessenger."
            )
        except (ImportError, AttributeError):
            logger.warning(
                f"Unable to import ControllerToServerMessenger from {plugin_path}. Using DefaultControllerToServerMessenger."
            )
        except Exception as e:
            logger.error(e)
            return

        plugin["ControllerToServerMessenger"] = ControllerToServerMessenger

    @classmethod
    @pluginnamefrompath
    def check_server_to_controller_messenger(
        cls, plugin_path: str, *, plugin_name=None
    ):
        """Check for the presence of a ServerToControllerMessenger module in the plugin's subdirectory.
        If found, import the module and create a dynamic plugin class that inherits from BaseServerToControllerMessenger and the plugin's ServerToControllerMessenger class.
        If not found, use the BaseServerToControllerMessenger class.
        """
        logger.info(
            f"Checking for ServerToControllerMessenger module in {plugin_path}..."
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
                    PluginServerToControllerMessenger,
                    BaseServerToControllerMessenger,
                ),
                {},
            )
        except ModuleNotFoundError:
            logger.info(
                f"No ServerToControllerMessenger module found for {plugin_path}. Using BaseServerToControllerMessenger."
            )
        except (ImportError, AttributeError):
            logger.warning(
                f"Unable to import ServerToControllerMessenger from {plugin_path}. Using BaseServerToControllerMessenger."
            )
        except Exception as e:
            logger.error(e)
            return

        plugin["ServerToControllerMessenger"] = ServerToControllerMessenger

    @classmethod
    @pluginnamefrompath
    def check_model(cls, plugin_path: str, *, plugin_name=None):
        logger.info(f"Checking for {plugin_path}.Model module.")
        try:
            model_module_name = f"{plugin_path}.Model"
            model_module = importlib.import_module(model_module_name)
        except ModuleNotFoundError:
            logger.info(f"No {plugin_name}.Model module found.")
            return
        except (ImportError, AttributeError) as e:
            logger.warning("Unable to import %s.Model - %s" % (plugin_name, e))
            return
        except Exception as e:
            logger.error("Unable to import %s.Model - %s" % (plugin_name, e))
            return

        model_class_name = utils.snakecase_to_pascalcase(plugin_name)
        if (
            plugin_name in Base.metadata.tables
            or model_class_name in Base.metadata.tables
        ):
            logger.info(f"Model for {plugin_name} already exists. Skipping.")
            return
        model_class_name = utils.snakecase_to_pascalcase(plugin_name)
        model_module.PluginModel = type(
            model_class_name,
            (
                model_module.PluginModel,
                Base,
            ),
            {
                "mqtt_id": Column(
                    Integer, ForeignKey("devices.mqtt_id", ondelete="CASCADE")
                ),
            },
        )
        Base.metadata.create_all(bind=engine)

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
            for x in ("db_session", "redis_session", "mqtt_client_session"):
                if x in dir(router_module):
                    setattr(router_module, x, getattr(dependencies, x).get())
            cls.ROUTERS.append(router_module.plugin_router)
        except ModuleNotFoundError:
            logger.info(f"No router module found for {plugin_name}.")
        except (ImportError, AttributeError):
            logger.warning(f"Unable to import router from {plugin_path}.")
        except Exception as e:
            logger.error(e)
            return

    @classmethod
    @pluginnamefrompath
    def check_extra_models(cls, plugin_path: str, *, plugin_name=None):
        """Check for the presence of extra models in the plugin's subdirectory.
        If found, import, and dynamically patch new models by combining the Base class with
        each of these extra models, using inheritance."""
        logger.info(f"Checking for {plugin_path}.models module.")
        try:
            models_module_name = f"{plugin_path}.models"
            models_module = importlib.import_module(models_module_name)
        except ModuleNotFoundError:
            logger.info("No %s.models module found." % (plugin_name))
            return
        except (ImportError, AttributeError) as e:
            logger.warning("Unable to import %s.Model - %s" % (plugin_name, e))
            return
        except Exception as e:
            logger.error("Unable to import %s.Model - %s" % (plugin_name, e))
            return

        if not hasattr(models_module, "models") or not models_module.models:
            logger.info(
                f"No models tuple found for {plugin_name}.models module. Skipping."
            )
            return

        for ExtraModel in models_module.models:
            ModelClassName = ExtraModel.__name__
            if (
                ExtraModel.__tablename__ in Base.metadata.tables
                or ModelClassName in Base.metadata.tables
            ):
                logger.info(
                    f"Model {ModelClassName} for {plugin_name} already exists. Skipping."
                )
                continue
            NewExtraModel = type(ModelClassName, (ExtraModel, Base), {})
            setattr(models_module, ModelClassName, NewExtraModel)
        Base.metadata.create_all(bind=engine)

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
            db_seeding_module.seed_db(dependencies.db_session.get())
        except ModuleNotFoundError:
            logger.info(f"No db_seeding module found for {plugin_name}.")
        except ImportError:
            logger.warning("Unable to import db_seeding from %s." % (plugin_path))
        except Exception as e:
            logger.error(e)
            return

    @classmethod
    def get_plugin_by_device_type_name(cls, plugin_name: str) -> dict:
        return cls.PLUGINS[plugin_name.lower()]
