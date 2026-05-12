import pytest

from src.plugins.manager.PluginsManager import (
    PluginsManager,
    PluginsMapper,
)


@pytest.fixture(scope="function", autouse=True)
def PluginsManager_cleanup():
    PluginsManager.PLUGINS = PluginsMapper()
    PluginsManager.ROUTERS = []
    yield
