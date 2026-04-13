import pytest


@pytest.fixture
def example_plugin_path():
    yield __file__.split(__name__)[0] + "example_plugin"
