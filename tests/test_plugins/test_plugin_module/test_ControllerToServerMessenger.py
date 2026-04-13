from unittest.mock import patch

from src.plugins import (
    BaseControllerToServerMessenger,
    DefaultControllerToServerMessenger,
    PluginsManager,
)


def test_PluginControllerTwoServerMessenger_subclassed_from_BaseControllerToServerMessenger(
    example_plugin_path,
):
    PluginsManager.add_plugin_object(example_plugin_path)
    PluginsManager.check_controller_to_server_messenger(example_plugin_path)
    PluginControllerTwoServerMessenger = PluginsManager.PLUGINS["example_plugin"][
        "ControllerToServerMessenger"
    ]
    assert issubclass(
        PluginControllerTwoServerMessenger, BaseControllerToServerMessenger
    )


def test_ModuleNotFoundError_exception_falls_back_on_BaseControllerToServerMessenger():
    with patch(
        "src.plugins.PluginsManager.importlib.import_module",
        return_value=ModuleNotFoundError(),
    ) as import_module:
        PluginsManager.add_plugin_object("test_plugin")
        PluginsManager.check_controller_to_server_messenger("test_plugin")
        import_module.assert_called_once_with("test_plugin.ControllerToServerMessenger")
        PluginControllerTwoServerMessenger = PluginsManager.PLUGINS["test_plugin"][
            "ControllerToServerMessenger"
        ]
        assert PluginControllerTwoServerMessenger is DefaultControllerToServerMessenger


def test_Exception_falls_back_on_BaseControllerToServerMessenger():
    with patch(
        "src.plugins.PluginsManager.importlib.import_module", return_value=Exception()
    ) as import_module:
        PluginsManager.add_plugin_object("test_plugin")
        PluginsManager.check_controller_to_server_messenger("test_plugin")
        import_module.assert_called_once_with("test_plugin.ControllerToServerMessenger")
        PluginControllerTwoServerMessenger = PluginsManager.PLUGINS["test_plugin"][
            "ControllerToServerMessenger"
        ]
        assert PluginControllerTwoServerMessenger is DefaultControllerToServerMessenger
