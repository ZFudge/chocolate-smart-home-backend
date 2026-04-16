import pytest


@pytest.fixture
def stateful_duplex_plugin_path():
    yield (__name__.rpartition(".")[0] + ".stateful_duplex_plugin")
