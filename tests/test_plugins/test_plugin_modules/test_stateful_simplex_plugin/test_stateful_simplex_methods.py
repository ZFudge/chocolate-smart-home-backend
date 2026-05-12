from unittest.mock import patch

from src.plugins import (
    BaseControllerToServerMessenger,
    BaseDeviceManager,
    BaseServerToControllerMessenger,
    DefaultControllerToServerMessenger,
    PluginsManager,
)

from .stateful_simplex_plugin.ControllerToServerMessenger import (
    ControllerToServerMessenger,
)
from .stateful_simplex_plugin.DeviceManager import (
    DeviceManager,
)


def test_stateful_simplex_ControllerToServerMessenger_subclassed_from_BaseControllerToServerMessenger(
    stateful_simplex_plugin_path, empty_test_db
):
    PluginsManager.load_plugin_from_path(stateful_simplex_plugin_path)
    StatefulSimplexPlugin = PluginsManager.PLUGINS["stateful_simplex_plugin"]
    PluginControllerToServerMessenger = StatefulSimplexPlugin[
        "ControllerToServerMessenger"
    ]
    assert issubclass(
        PluginControllerToServerMessenger, BaseControllerToServerMessenger
    )
    assert issubclass(PluginControllerToServerMessenger, ControllerToServerMessenger)


def test_stateful_simplex_DeviceManager_is_BaseDeviceManager(
    stateful_simplex_plugin_path, empty_test_db
):
    PluginsManager.load_plugin_from_path(stateful_simplex_plugin_path)

    StatefulSimplexPlugin = PluginsManager.PLUGINS["stateful_simplex_plugin"]
    PluginDeviceManager = StatefulSimplexPlugin["DeviceManager"]
    assert issubclass(PluginDeviceManager, BaseDeviceManager)
    assert issubclass(PluginDeviceManager, DeviceManager)


def test_stateful_simplex_ServerToControllerMessenger_is_BaseServerToControllerMessenger(
    stateful_simplex_plugin_path, empty_test_db
):
    PluginsManager.load_plugin_from_path(stateful_simplex_plugin_path)
    assert (
        PluginsManager.PLUGINS["stateful_simplex_plugin"]["ServerToControllerMessenger"]
        is BaseServerToControllerMessenger
    )


def test_stateful_simplex_ModuleNotFoundError_exception_falls_back_on_DefaultControllerToServerMessenger(
    stateful_simplex_plugin_path,
):
    with patch(
        "src.plugins.manager.utils.importlib.import_module",
        side_effect=ModuleNotFoundError(),
    ):
        PluginsManager.map_new_plugin(stateful_simplex_plugin_path)
        PluginsManager.check_server_to_controller_messenger(
            stateful_simplex_plugin_path
        )
        assert (
            PluginsManager.PLUGINS["stateful_simplex_plugin"][
                "ControllerToServerMessenger"
            ]
            is DefaultControllerToServerMessenger
        )


def test_stateful_simplex_Exception_falls_back_on_DefaultControllerToServerMessenger(
    stateful_simplex_plugin_path,
):
    with patch(
        "src.plugins.manager.utils.importlib.import_module", side_effect=Exception()
    ):
        PluginsManager.map_new_plugin(stateful_simplex_plugin_path)
        PluginsManager.check_server_to_controller_messenger(
            stateful_simplex_plugin_path
        )
        assert (
            PluginsManager.PLUGINS["stateful_simplex_plugin"][
                "ControllerToServerMessenger"
            ]
            is DefaultControllerToServerMessenger
        )
