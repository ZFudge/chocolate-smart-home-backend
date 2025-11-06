import logging

from src.plugins.base_device_manager import BaseDeviceManager


logger = logging.getLogger()


class LeonardoDeviceManager(BaseDeviceManager):
    """Manage "leonardo" and "devices" table rows using incoming device data."""


# Alias OnOffDeviceManager for use in ..discovered_plugins.DISCOVERED_PLUGINS["on_off"] dict
DeviceManager = LeonardoDeviceManager
