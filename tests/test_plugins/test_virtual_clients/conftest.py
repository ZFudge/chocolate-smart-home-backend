from types import ModuleType
from typing import Tuple

import pytest

from src.plugins.virtual_clients import DiscoverVirtualClients


@pytest.fixture(scope="function", autouse=True)
def DiscoverVirtualClients_cleanup():
    DiscoverVirtualClients.mqtt_id = 900
    DiscoverVirtualClients.compose_funcs_mapping = {}
    DiscoverVirtualClients.virtual_clients = {}
    yield


@pytest.fixture
def vcs_module():
    seeds = [
        {"name": "Test Virtual Client 0"},
        {"name": "Test Virtual Client 1"},
        {"name": "Test Virtual Client 2"},
    ]
    test_module = ModuleType(
        name="test_module",
    )
    test_module.seeds = seeds

    def t(seed: dict) -> str:
        return ""

    def p(payload: str) -> Tuple[None, None]:
        return payload.split("=")

    test_module.compose_state_as_msg = t
    test_module.parse_payload = p
    yield test_module
