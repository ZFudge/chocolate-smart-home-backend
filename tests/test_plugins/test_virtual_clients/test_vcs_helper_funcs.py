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


def test_validate_virtual_client_module_parse_incoming_payload_not_callable(vcs_module):
    setattr(vcs_module, "parse_incoming_payload", None)
    assert not validate_virtual_client_module(vcs_module)
    setattr(vcs_module, "parse_incoming_payload", 1)
    assert not validate_virtual_client_module(vcs_module)
    setattr(vcs_module, "parse_incoming_payload", "string")
    assert not validate_virtual_client_module(vcs_module)
    setattr(vcs_module, "parse_incoming_payload", 1.0)
    assert not validate_virtual_client_module(vcs_module)
    setattr(vcs_module, "parse_incoming_payload", True)
    assert not validate_virtual_client_module(vcs_module)


def test_validate_virtual_client_module_parse_incoming_payload_signature_invalid(
    vcs_module,
):
    setattr(vcs_module, "parse_incoming_payload", lambda: "cabbage")
    assert not validate_virtual_client_module(vcs_module)

    # invalid return annotation
    def parse_incoming_payload(payload: str) -> str:
        pass

    setattr(vcs_module, "parse_incoming_payload", parse_incoming_payload)

    # invalid parameter annotation
    def parse_incoming_payload(payload: int) -> tuple[None, None]:
        pass

    setattr(vcs_module, "parse_incoming_payload", parse_incoming_payload)
    assert not validate_virtual_client_module(vcs_module)

    # fewer than 2 elements in tuple annotation
    def parse_incoming_payload(payload: str) -> tuple[None]:
        pass

    setattr(vcs_module, "parse_incoming_payload", parse_incoming_payload)
    assert not validate_virtual_client_module(vcs_module)

    # more than 2 elements in tuple annotation
    def parse_incoming_payload(payload: str) -> tuple[None, None, None]:
        pass

    setattr(vcs_module, "parse_incoming_payload", parse_incoming_payload)
    assert not validate_virtual_client_module(vcs_module)


def test_validate_virtual_client_module_parse_incoming_payload_signature_valid(
    vcs_module,
):
    def parse_incoming_payload(payload: str) -> tuple[None, None]:
        pass

    setattr(vcs_module, "parse_incoming_payload", parse_incoming_payload)
    assert validate_virtual_client_module(vcs_module)

    def parse_incoming_payload(payload: str) -> tuple[str, str]:
        pass

    setattr(vcs_module, "parse_incoming_payload", parse_incoming_payload)
    assert validate_virtual_client_module(vcs_module)

    def parse_incoming_payload(payload: str) -> tuple[bool, bool]:
        pass

    setattr(vcs_module, "parse_incoming_payload", parse_incoming_payload)
    assert validate_virtual_client_module(vcs_module)


def test_validate_virtual_client_module_invalid_compose_outgoing_msg(
    vcs_module,
):
    setattr(vcs_module, "compose_outgoing_msg", None)
    assert not validate_virtual_client_module(vcs_module)
    setattr(vcs_module, "compose_outgoing_msg", 1)
    assert not validate_virtual_client_module(vcs_module)
    setattr(vcs_module, "compose_outgoing_msg", "string")
    assert not validate_virtual_client_module(vcs_module)
    setattr(vcs_module, "compose_outgoing_msg", 1.0)
    assert not validate_virtual_client_module(vcs_module)
    setattr(vcs_module, "compose_outgoing_msg", True)
    assert not validate_virtual_client_module(vcs_module)


def test_validate_virtual_client_module_missing_only_seeds(
    vcs_module,
):
    delattr(vcs_module, "seeds")
    assert not validate_virtual_client_module(vcs_module)


def test_validate_virtual_client_module_still_passes_without_compose_outgoing_msg(
    vcs_module,
):
    delattr(vcs_module, "compose_outgoing_msg")
    assert validate_virtual_client_module(vcs_module)


def test_validate_virtual_client_module_still_passes_without_parse_incoming_payload(
    vcs_module,
):
    delattr(vcs_module, "parse_incoming_payload")
    assert validate_virtual_client_module(vcs_module)


def test_import_vcs_module_returns_none_if_module_does_not_exist():
    assert import_vcs_module("does_not_exist") is None
