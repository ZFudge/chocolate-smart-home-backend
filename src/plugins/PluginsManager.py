import importlib
import logging
from types import ModuleType

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
        """
        Dynamically creates a new class that inherits from the plugin's
        DeviceManager class and the BaseDeviceManager.
        If a plugin class is not found, use the BaseDeviceManager class.
        """
        device_manager_module: ModuleType | None = import_plugin_module(
            plugin_path, "DeviceManager"
        )
        DeviceManager = BaseDeviceManager
        if has_valid_callable(device_manager_module, "DeviceManager"):
            DeviceManager = type(
                "DeviceManager",
                (
                    device_manager_module.DeviceManager,
                    BaseDeviceManager,
                ),
                {},
            )
        plugin = cls.PLUGINS[plugin_name]
        plugin["DeviceManager"] = DeviceManager

    @classmethod
    @pluginnamefrompath
    def check_controller_to_server_messenger(
        cls, plugin_path: str, *, plugin_name=None
    ):
        """
        Dynamically creates a new class that inherits from the plugin's
        ControllerToServerMessenger class and DefaultControllerToServerMessenger.
        If a plugin class not found, use the DefaultControllerToServerMessenger class.
        """
        ctos_module: ModuleType | None = import_plugin_module(
            plugin_path, "ControllerToServerMessenger"
        )
        if not isinstance(ctos_module, ModuleType):
            logger.info("Using DefaultControllerToServerMessenger.")
            ControllerToServerMessenger = DefaultControllerToServerMessenger
        else:
            PluginControllerToServerMessenger = ctos_module.ControllerToServerMessenger
            _BaseControllerToServerMessenger = BaseControllerToServerMessenger
            # if plugin device does not have its own device-specific values to parse,
            # defer to DefaultControllerToServerMessenger to be sure parse_controller_msg returns a device schema
            if not has_valid_callable(
                PluginControllerToServerMessenger, "parse_controller_msg"
            ):
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

        plugin = cls.PLUGINS[plugin_name]
        plugin["ControllerToServerMessenger"] = ControllerToServerMessenger

    @classmethod
    @pluginnamefrompath
    def check_server_to_controller_messenger(
        cls, plugin_path: str, *, plugin_name=None
    ):
        """
        Dynamically creates a new class that inherits from the plugin's
        ServerToControllerMessenger class and BaseServerToControllerMessenger.
        If a plugin class not found, use the BaseServerToControllerMessenger
        class.
        """
        stoc_module: ModuleType | None = import_plugin_module(
            plugin_path, "ServerToControllerMessenger"
        )
        ServerToControllerMessenger = BaseServerToControllerMessenger
        if isinstance(stoc_module, ModuleType) and has_valid_callable(
            stoc_module, "ServerToControllerMessenger"
        ):
            ServerToControllerMessenger = type(
                "ServerToControllerMessenger",
                (
                    stoc_module.ServerToControllerMessenger,
                    BaseServerToControllerMessenger,
                ),
                {},
            )
        else:
            logger.info(f"{plugin_name} using BaseServerToControllerMessenger")
        plugin = cls.PLUGINS[plugin_name]
        plugin["ServerToControllerMessenger"] = ServerToControllerMessenger

    @classmethod
    @pluginnamefrompath
    def check_model(cls, plugin_path: str, *, plugin_name=None):
        """
        Dynamically creates a new model class that inherits from the plugin's
        PluginModel class and the database Base class.
        """
        model_module: ModuleType | None = import_plugin_module(plugin_path, "Model")
        if not has_valid_callable(model_module, "PluginModel"):
            if isinstance(model_module, ModuleType):
                logger.info(
                    f'{plugin_name}.Model module exists but does not have a valid "PluginModel" class.'
                )
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
    def check_router(cls, plugin_path: str):
        """
        Expose dependencies to router endpoints and add router to the PluginsManager.ROUTERS list.
        """
        router_module: ModuleType | None = import_plugin_module(plugin_path, "router")
        if not isinstance(router_module, ModuleType):
            return
        dependency_names = ("db_session", "redis_session", "mqtt_client_session")
        for dn in dependency_names:
            if dn in dir(router_module):
                setattr(router_module, dn, getattr(dependencies, dn).get())
        cls.ROUTERS.append(router_module.plugin_router)

    @classmethod
    @pluginnamefrompath
    def check_extra_models(cls, plugin_path: str, *, plugin_name=None):
        """
        Dynamically create new model classes by inheriting from the
        plugin's extra model classes and the database Base class.
        """
        models_module: ModuleType | None = import_plugin_module(plugin_path, "models")
        if not isinstance(models_module, ModuleType) or not hasattr(
            models_module, "models"
        ):
            return

        for ExtraModel in models_module.models:
            ModelClassName = ExtraModel.__name__
            if (
                ExtraModel.__tablename__ in Base.metadata.tables
                or ModelClassName in Base.metadata.tables
            ):
                logger.info(
                    f"{plugin_name} model {ModelClassName} already exists.ms Skipping."
                )
                continue
            NewExtraModel = type(ModelClassName, (ExtraModel, Base), {})
            setattr(models_module, ModelClassName, NewExtraModel)
        Base.metadata.create_all(bind=engine)

    @classmethod
    @pluginnamefrompath
    def check_db_seeding(cls, plugin_path: str, *, plugin_name=None):
        """Seeds values into the database."""
        db_seeding_module = import_plugin_module(plugin_path, "db_seeding")
        if not has_valid_callable(db_seeding_module, "seed_db"):
            if isinstance(db_seeding_module, ModuleType):
                logger.info(
                    f'{plugin_name}.db_seeding module exists but does not have a valid "seed_db" function.'
                )
            return
        db_seeding_module.seed_db(dependencies.db_session.get())

    @classmethod
    def get_plugin_by_device_type_name(cls, plugin_name: str) -> dict:
        return cls.PLUGINS[plugin_name.lower()]
