from unittest.mock import patch

from src.plugins import (
    BaseDeviceManager,
    BaseServerToControllerMessenger,
    DefaultControllerToServerMessenger,
    PluginsManager,
)

from .stateless_simplex_plugin.ServerToControllerMessenger import (
    ServerToControllerMessenger,
)


def test_stateless_simplex_ServerToControllerMessenger_subclassed_from_BaseServerToControllerMessenger(
    stateless_simplex_plugin_path,
):
    PluginsManager.load_plugin_from_path(stateless_simplex_plugin_path)
    StatelessSimplexPlugin = PluginsManager.PLUGINS["stateless_simplex_plugin"]
    PluginServerToControllerMessenger = StatelessSimplexPlugin[
        "ServerToControllerMessenger"
    ]
    assert issubclass(
        PluginServerToControllerMessenger, BaseServerToControllerMessenger
    )
    assert issubclass(PluginServerToControllerMessenger, ServerToControllerMessenger)


def test_stateless_simplex_DeviceManager_is_BaseDeviceManager(
    stateless_simplex_plugin_path,
):
    PluginsManager.load_plugin_from_path(stateless_simplex_plugin_path)

    assert (
        PluginsManager.PLUGINS["stateless_simplex_plugin"]["DeviceManager"]
        is BaseDeviceManager
    )


def test_stateless_simplex_ControllerToServerMessenger_is_DefaultControllerToServerMessenger(
    stateless_simplex_plugin_path,
):
    PluginsManager.load_plugin_from_path(stateless_simplex_plugin_path)
    assert (
        PluginsManager.PLUGINS["stateless_simplex_plugin"][
            "ControllerToServerMessenger"
        ]
        is DefaultControllerToServerMessenger
    )


def test_stateless_simplex_ModuleNotFoundError_exception_falls_back_on_BaseServerToControllerMessenger(
    stateless_simplex_plugin_path,
):
    with patch(
        "src.plugins.PluginsManager.importlib.import_module",
        side_effect=ModuleNotFoundError(),
    ):
        PluginsManager.map_new_plugin(stateless_simplex_plugin_path)
        PluginsManager.check_server_to_controller_messenger(
            stateless_simplex_plugin_path
        )
        assert (
            PluginsManager.PLUGINS["stateless_simplex_plugin"][
                "ServerToControllerMessenger"
            ]
            is BaseServerToControllerMessenger
        )


def test_stateless_simplex_Exception_falls_back_on_BaseServerToControllerMessenger(
    stateless_simplex_plugin_path,
):
    with patch(
        "src.plugins.PluginsManager.importlib.import_module", side_effect=Exception()
    ):
        PluginsManager.map_new_plugin(stateless_simplex_plugin_path)
        PluginsManager.check_server_to_controller_messenger(
            stateless_simplex_plugin_path
        )
        assert (
            PluginsManager.PLUGINS["stateless_simplex_plugin"][
                "ServerToControllerMessenger"
            ]
            is BaseServerToControllerMessenger
        )
