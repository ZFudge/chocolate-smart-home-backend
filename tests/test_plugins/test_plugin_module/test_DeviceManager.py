from unittest.mock import patch

from src.plugins import BaseDeviceManager, PluginsManager


def test_PluginDeviceManager_is_subclass_of_BaseDeviceManager(example_plugin_path):
    PluginsManager.add_plugin_object(example_plugin_path)
    PluginsManager.check_device_manager(example_plugin_path)
    PluginDeviceManager = PluginsManager.PLUGINS["example_plugin"]["DeviceManager"]
    assert issubclass(PluginDeviceManager, BaseDeviceManager)


def test_ModuleNotFoundError_exception_falls_back_on_BaseDeviceManager():
    with patch(
        "src.plugins.PluginsManager.importlib.import_module",
        return_value=ModuleNotFoundError(),
    ) as import_module:
        PluginsManager.add_plugin_object("test_plugin")
        PluginsManager.check_device_manager("test_plugin")
        import_module.assert_called_once_with("test_plugin.DeviceManager")
        PluginDeviceManager = PluginsManager.PLUGINS["test_plugin"]["DeviceManager"]
        assert PluginDeviceManager is BaseDeviceManager


def test_Exception_falls_back_on_BaseDeviceManager():
    with patch(
        "src.plugins.PluginsManager.importlib.import_module", return_value=Exception()
    ) as import_module:
        PluginsManager.add_plugin_object("test_plugin")
        PluginsManager.check_device_manager("test_plugin")
        import_module.assert_called_once_with("test_plugin.DeviceManager")
        PluginDeviceManager = PluginsManager.PLUGINS["test_plugin"]["DeviceManager"]
        assert PluginDeviceManager is BaseDeviceManager
