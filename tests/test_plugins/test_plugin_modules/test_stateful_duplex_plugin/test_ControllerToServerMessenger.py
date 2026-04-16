from unittest.mock import patch

from src.plugins import (
    BaseControllerToServerMessenger,
    DefaultControllerToServerMessenger,
    PluginsManager,
)

from .stateful_duplex_plugin.ControllerToServerMessenger import (
    ControllerToServerMessenger,
)


def test_stateful_duplex_PluginControllerToServerMessenger_subclassed_from_BaseControllerToServerMessenger(
    stateful_duplex_plugin_path,
):
    PluginsManager.map_new_plugin(stateful_duplex_plugin_path)
    PluginsManager.check_controller_to_server_messenger(stateful_duplex_plugin_path)
    PluginControllerToServerMessenger = PluginsManager.PLUGINS[
        "stateful_duplex_plugin"
    ]["ControllerToServerMessenger"]
    assert issubclass(
        PluginControllerToServerMessenger, BaseControllerToServerMessenger
    )
    assert issubclass(PluginControllerToServerMessenger, ControllerToServerMessenger)


def test_stateful_duplex_ModuleNotFoundError_exception_falls_back_on_BaseControllerToServerMessenger():
    with patch(
        "src.plugins.PluginsManager.importlib.import_module",
        return_value=ModuleNotFoundError(),
    ) as import_module:
        PluginsManager.map_new_plugin("test_plugin")
        PluginsManager.check_controller_to_server_messenger("test_plugin")
        import_module.assert_called_once_with("test_plugin.ControllerToServerMessenger")
        PluginControllerToServerMessenger = PluginsManager.PLUGINS["test_plugin"][
            "ControllerToServerMessenger"
        ]
        assert PluginControllerToServerMessenger is DefaultControllerToServerMessenger


def test_stateful_duplex_Exception_falls_back_on_BaseControllerToServerMessenger():
    with patch(
        "src.plugins.PluginsManager.importlib.import_module", return_value=Exception()
    ) as import_module:
        PluginsManager.map_new_plugin("test_plugin")
        PluginsManager.check_controller_to_server_messenger("test_plugin")
        import_module.assert_called_once_with("test_plugin.ControllerToServerMessenger")
        PluginControllerToServerMessenger = PluginsManager.PLUGINS["test_plugin"][
            "ControllerToServerMessenger"
        ]
        assert PluginControllerToServerMessenger is DefaultControllerToServerMessenger
