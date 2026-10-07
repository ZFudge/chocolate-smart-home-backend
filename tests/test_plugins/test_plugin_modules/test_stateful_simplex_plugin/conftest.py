import pytest


@pytest.fixture
def stateful_simplex_plugin_path():
    yield (__name__.rpartition(".")[0] + ".stateful_simplex_plugin")
