from unittest.mock import patch

from src.plugins import BaseServerToControllerMessenger, PluginsManager

from .stateful_duplex_plugin.ServerToControllerMessenger import (
    ServerToControllerMessenger,
)


def test_stateful_duplex_PluginServerToControllerMessenger_subclassed_from_BaseServerToControllerMessenger(
    stateful_duplex_plugin_path,
):
    PluginsManager.map_new_plugin(stateful_duplex_plugin_path)
    PluginsManager.check_server_to_controller_messenger(stateful_duplex_plugin_path)
    PluginServerToControllerMessenger = PluginsManager.PLUGINS[
        "stateful_duplex_plugin"
    ]["ServerToControllerMessenger"]
    assert issubclass(
        PluginServerToControllerMessenger, BaseServerToControllerMessenger
    )
    assert issubclass(PluginServerToControllerMessenger, ServerToControllerMessenger)


def test_stateful_duplex_ModuleNotFoundError_exception_falls_back_on_BaseServerToControllerMessenger():
    with patch(
        "src.plugins.manager.utils.importlib.import_module",
        return_value=ModuleNotFoundError(),
    ) as import_module:
        PluginsManager.map_new_plugin("test_plugin")
        PluginsManager.check_server_to_controller_messenger("test_plugin")
        import_module.assert_called_once_with("test_plugin.ServerToControllerMessenger")
        PluginServerToControllerMessenger = PluginsManager.PLUGINS["test_plugin"][
            "ServerToControllerMessenger"
        ]
        assert PluginServerToControllerMessenger is BaseServerToControllerMessenger


def test_stateful_duplex_Exception_falls_back_on_BaseServerToControllerMessenger():
    with patch(
        "src.plugins.manager.utils.importlib.import_module", return_value=Exception()
    ) as import_module:
        PluginsManager.map_new_plugin("test_plugin")
        PluginsManager.check_server_to_controller_messenger("test_plugin")
        import_module.assert_called_once_with("test_plugin.ServerToControllerMessenger")
        PluginServerToControllerMessenger = PluginsManager.PLUGINS["test_plugin"][
            "ServerToControllerMessenger"
        ]
        assert PluginServerToControllerMessenger is BaseServerToControllerMessenger
