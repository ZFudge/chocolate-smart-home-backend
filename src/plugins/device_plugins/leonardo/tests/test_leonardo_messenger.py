import pytest

from src.plugins.device_plugins.leonardo.duplex_messenger import LeonardoDuplexMessenger


def test_leonardo_compose_msg_dict():
    assert LeonardoDuplexMessenger().compose_msg({"command": "move"}) == "move"
    assert LeonardoDuplexMessenger().compose_msg({"command": "lock"}) == "lock"
    assert LeonardoDuplexMessenger().compose_msg({"command": "unlock"}) == "unlock"
    assert LeonardoDuplexMessenger().compose_msg({"command": "talon"}) == "talon"


def test_leonardo_compose_msg__invalid_message():
    with pytest.raises(ValueError):
        LeonardoDuplexMessenger().compose_msg("invalid")
    with pytest.raises(ValueError):
        LeonardoDuplexMessenger().compose_msg(None)
    with pytest.raises(ValueError):
        LeonardoDuplexMessenger().compose_msg(123)
    with pytest.raises(ValueError):
        LeonardoDuplexMessenger().compose_msg(True)
    with pytest.raises(ValueError):
        LeonardoDuplexMessenger().compose_msg(False)
    with pytest.raises(ValueError):
        LeonardoDuplexMessenger().compose_msg([])
    with pytest.raises(ValueError):
        LeonardoDuplexMessenger().compose_msg({})


def test_leonardo_compose_msg_dict__invalid_message():
    with pytest.raises(ValueError):
        LeonardoDuplexMessenger().compose_msg({"command": "invalid"})
    with pytest.raises(ValueError):
        LeonardoDuplexMessenger().compose_msg({"command": None})
    with pytest.raises(ValueError):
        LeonardoDuplexMessenger().compose_msg({"command": 123})
    with pytest.raises(ValueError):
        LeonardoDuplexMessenger().compose_msg({"command": True})
    with pytest.raises(ValueError):
        LeonardoDuplexMessenger().compose_msg({"command": False})
