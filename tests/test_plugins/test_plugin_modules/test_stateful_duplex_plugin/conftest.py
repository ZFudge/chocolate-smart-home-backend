import pytest
from fastapi import FastAPI


@pytest.fixture
def stateful_duplex_plugin_path():
    yield (__name__.rpartition(".")[0] + ".stateful_duplex_plugin")


@pytest.fixture
def test_app():
    yield FastAPI()
