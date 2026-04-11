from types import ModuleType

import pytest

from src.plugins.virtual_clients.helper_funcs import validate_virtual_client_module


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


def test_validate_virtual_client_module_none():
    assert not validate_virtual_client_module(None)


def test_validate_virtual_client_module_invalid_seeds(vcs_module):
    setattr(vcs_module, "seeds", None)
    assert not validate_virtual_client_module(vcs_module)
    setattr(vcs_module, "seeds", 1)
    assert not validate_virtual_client_module(vcs_module)
    setattr(vcs_module, "seeds", "string")
    assert not validate_virtual_client_module(vcs_module)
    setattr(vcs_module, "seeds", 1.0)
    assert not validate_virtual_client_module(vcs_module)
    setattr(vcs_module, "seeds", True)
    assert not validate_virtual_client_module(vcs_module)


def test_validate_virtual_client_module_missing_only_translate_vc_dict_to_mqtt_msg(
    vcs_module,
):
    delattr(vcs_module, "translate_vc_dict_to_mqtt_msg")
    assert not validate_virtual_client_module(vcs_module)


def test_validate_virtual_client_module_missing_only_parse_payload(vcs_module):
    delattr(vcs_module, "parse_payload")
    assert not validate_virtual_client_module(vcs_module)
