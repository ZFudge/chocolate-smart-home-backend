import pytest


@pytest.fixture
def stateless_simplex_plugin_path():
    yield (__name__.rpartition(".")[0] + ".stateless_simplex_plugin")
