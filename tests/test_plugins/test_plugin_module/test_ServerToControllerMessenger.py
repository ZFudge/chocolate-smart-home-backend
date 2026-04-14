from unittest.mock import patch

from src.plugins import BaseServerToControllerMessenger, PluginsManager

from .example_plugin.ServerToControllerMessenger import ServerToControllerMessenger


def test_PluginServerToControllerMessenger_subclassed_from_BaseServerToControllerMessenger(
    example_plugin_path,
):
    PluginsManager.add_plugin_object(example_plugin_path)
    PluginsManager.check_server_to_controller_messenger(example_plugin_path)
    PluginServerToControllerMessenger = PluginsManager.PLUGINS["example_plugin"][
        "ServerToControllerMessenger"
    ]
    assert issubclass(
        PluginServerToControllerMessenger, BaseServerToControllerMessenger
    )
    assert issubclass(PluginServerToControllerMessenger, ServerToControllerMessenger)


def test_ModuleNotFoundError_exception_falls_back_on_BaseServerToControllerMessenger():
    with patch(
        "src.plugins.PluginsManager.importlib.import_module",
        return_value=ModuleNotFoundError(),
    ) as import_module:
        PluginsManager.add_plugin_object("test_plugin")
        PluginsManager.check_server_to_controller_messenger("test_plugin")
        import_module.assert_called_once_with("test_plugin.ServerToControllerMessenger")
        PluginServerToControllerMessenger = PluginsManager.PLUGINS["test_plugin"][
            "ServerToControllerMessenger"
        ]
        assert PluginServerToControllerMessenger is BaseServerToControllerMessenger


def test_Exception_falls_back_on_BaseServerToControllerMessenger():
    with patch(
        "src.plugins.PluginsManager.importlib.import_module", return_value=Exception()
    ) as import_module:
        PluginsManager.add_plugin_object("test_plugin")
        PluginsManager.check_server_to_controller_messenger("test_plugin")
        import_module.assert_called_once_with("test_plugin.ServerToControllerMessenger")
        PluginServerToControllerMessenger = PluginsManager.PLUGINS["test_plugin"][
            "ServerToControllerMessenger"
        ]
        assert PluginServerToControllerMessenger is BaseServerToControllerMessenger
