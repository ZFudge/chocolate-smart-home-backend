from types import ModuleType

import pytest

from src.plugins.virtual_clients import DiscoverVirtualClients


@pytest.fixture(scope="function", autouse=True)
def DiscoverVirtualClients_cleanup():
    DiscoverVirtualClients.mqtt_id = 900
    DiscoverVirtualClients.translate_vc_state_to_msg_func_mapping = {}
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
    test_module.translate_vc_dict_to_mqtt_msg = lambda _: None
    test_module.parse_payload = lambda _: None
    yield test_module
