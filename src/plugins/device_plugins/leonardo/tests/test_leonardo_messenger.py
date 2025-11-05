import pytest

from src.plugins.device_plugins.leonardo.duplex_messenger import (
    LeonardoDuplexMessenger
)
from src.schemas import DeviceReceived


def test_leonardo_serialize():
    expected_serialized_data_dict = {
        "online": True,
        "mqtt_id": 123,
        "name": None,
        "device_type_name": "leonardo",
        "remote_name": "Remote Name - uid",
    }

    device_data = DeviceReceived(
        mqtt_id=123,
        device_type_name="leonardo",
        remote_name="Remote Name - uid",
    )
    serialized_data = LeonardoDuplexMessenger().serialize(device_data)

    assert serialized_data == expected_serialized_data_dict


def test_leonardo_compose_msg_str():
    assert LeonardoDuplexMessenger().compose_msg("wake") == "wake"
    assert LeonardoDuplexMessenger().compose_msg("lock") == "lock"
    assert LeonardoDuplexMessenger().compose_msg("unlock") == "unlock"
    assert LeonardoDuplexMessenger().compose_msg("talon") == "talon"


def test_leonardo_compose_msg_dict():
    assert LeonardoDuplexMessenger().compose_msg({"msg": "wake"}) == "wake"
    assert LeonardoDuplexMessenger().compose_msg({"msg": "lock"}) == "lock"
    assert LeonardoDuplexMessenger().compose_msg({"msg": "unlock"}) == "unlock"
    assert LeonardoDuplexMessenger().compose_msg({"msg": "talon"}) == "talon"


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
        LeonardoDuplexMessenger().compose_msg({"msg": "invalid"})
    with pytest.raises(ValueError):
        LeonardoDuplexMessenger().compose_msg({"msg": None})
    with pytest.raises(ValueError):
        LeonardoDuplexMessenger().compose_msg({"msg": 123})
    with pytest.raises(ValueError):
        LeonardoDuplexMessenger().compose_msg({"msg": True})
    with pytest.raises(ValueError):
        LeonardoDuplexMessenger().compose_msg({"msg": False})
