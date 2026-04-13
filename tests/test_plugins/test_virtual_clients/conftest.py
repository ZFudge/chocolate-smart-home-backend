from types import ModuleType
from typing import Tuple

import pytest

from src.plugins.virtual_clients import VirtualClientsManager


@pytest.fixture(scope="function", autouse=True)
def VirtualClientsManager_cleanup():
    VirtualClientsManager.mqtt_id = 900
    VirtualClientsManager.outgoing_msg_composer_funcs = {}
    VirtualClientsManager.virtual_clients = {}
    yield


@pytest.fixture
def vcs_module():
    seeds = [
        {"name": "Test Virtual Client 0"},
        {"name": "Test Virtual Client 1"},
        {"name": "Test Virtual Client 2"},
    ]
    test_vcs_module = ModuleType(
        name="test_vcs_module",
    )
    test_vcs_module.seeds = seeds

    def composer(seed: dict) -> str:
        return ""

    test_vcs_module.compose_outgoing_msg = composer

    def parser(payload: str) -> Tuple[None, None]:
        return payload.split("=")

    test_vcs_module.parse_incoming_payload = parser

    yield test_vcs_module
