import logging

from ..bases import (
    BaseDeviceManager,
    BaseServerToControllerMessenger,
    DefaultControllerToServerMessenger,
)


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
