from unittest.mock import patch

from src.plugins import BaseDeviceManager, PluginsManager


def test_stateful_duplex_PluginDeviceManager_is_subclass_of_BaseDeviceManager(
    stateful_duplex_plugin_path,
):
    PluginsManager.map_new_plugin(stateful_duplex_plugin_path)
    PluginsManager.check_device_manager(stateful_duplex_plugin_path)
    PluginDeviceManager = PluginsManager.PLUGINS["stateful_duplex_plugin"][
        "DeviceManager"
    ]
    assert issubclass(PluginDeviceManager, BaseDeviceManager)


def test_stateful_duplex_ModuleNotFoundError_exception_falls_back_on_BaseDeviceManager():
    with patch(
        "src.plugins.PluginsManager.importlib.import_module",
        return_value=ModuleNotFoundError(),
    ) as import_module:
        PluginsManager.map_new_plugin("test_plugin")
        PluginsManager.check_device_manager("test_plugin")
        import_module.assert_called_once_with("test_plugin.DeviceManager")
        PluginDeviceManager = PluginsManager.PLUGINS["test_plugin"]["DeviceManager"]
        assert PluginDeviceManager is BaseDeviceManager


def test_stateful_duplex_Exception_falls_back_on_BaseDeviceManager():
    with patch(
        "src.plugins.PluginsManager.importlib.import_module", return_value=Exception()
    ) as import_module:
        PluginsManager.map_new_plugin("test_plugin")
        PluginsManager.check_device_manager("test_plugin")
        import_module.assert_called_once_with("test_plugin.DeviceManager")
        PluginDeviceManager = PluginsManager.PLUGINS["test_plugin"]["DeviceManager"]
        assert PluginDeviceManager is BaseDeviceManager
