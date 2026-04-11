from src.plugins.virtual_clients.helper_funcs import (
    import_vcs_module,
    validate_virtual_client_module,
)


def test_validate_virtual_client_module_passes(vcs_module):
    assert validate_virtual_client_module(vcs_module)


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


def test_validate_virtual_client_module_invalid_parse_payload(vcs_module):
    setattr(vcs_module, "parse_payload", None)
    assert not validate_virtual_client_module(vcs_module)
    setattr(vcs_module, "parse_payload", 1)
    assert not validate_virtual_client_module(vcs_module)
    setattr(vcs_module, "parse_payload", "string")
    assert not validate_virtual_client_module(vcs_module)
    setattr(vcs_module, "parse_payload", 1.0)
    assert not validate_virtual_client_module(vcs_module)
    setattr(vcs_module, "parse_payload", True)
    assert not validate_virtual_client_module(vcs_module)


def test_validate_virtual_client_module_invalid_translate_vc_dict_to_mqtt_msg(
    vcs_module,
):
    setattr(vcs_module, "translate_vc_dict_to_mqtt_msg", None)
    assert not validate_virtual_client_module(vcs_module)
    setattr(vcs_module, "translate_vc_dict_to_mqtt_msg", 1)
    assert not validate_virtual_client_module(vcs_module)
    setattr(vcs_module, "translate_vc_dict_to_mqtt_msg", "string")
    assert not validate_virtual_client_module(vcs_module)
    setattr(vcs_module, "translate_vc_dict_to_mqtt_msg", 1.0)
    assert not validate_virtual_client_module(vcs_module)
    setattr(vcs_module, "translate_vc_dict_to_mqtt_msg", True)
    assert not validate_virtual_client_module(vcs_module)


def test_validate_virtual_client_module_missing_only_seeds(
    vcs_module,
):
    delattr(vcs_module, "seeds")
    assert not validate_virtual_client_module(vcs_module)


def test_validate_virtual_client_module_missing_only_translate_vc_dict_to_mqtt_msg(
    vcs_module,
):
    delattr(vcs_module, "translate_vc_dict_to_mqtt_msg")
    assert not validate_virtual_client_module(vcs_module)


def test_validate_virtual_client_module_missing_only_parse_payload(vcs_module):
    delattr(vcs_module, "parse_payload")
    assert not validate_virtual_client_module(vcs_module)


def test_import_vcs_module_returns_none_if_module_does_not_exist():
    assert import_vcs_module("does_not_exist") is None
