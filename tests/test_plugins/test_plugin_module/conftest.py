import pytest


@pytest.fixture
def example_plugin_path():
    yield (__name__.rpartition(".")[0] + ".example_plugin")
