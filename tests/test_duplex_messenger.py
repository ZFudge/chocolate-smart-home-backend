import pytest

from chocolate_smart_home.plugins.base_duplex_messenger import (
    BaseDuplexMessenger,
    DefaultDuplexMessenger,
)


def test_parse_msg():
    duplex_messenger = BaseDuplexMessenger()

    msg = "1,device_type_name,remote_name - 1"
    device_data, _ = duplex_messenger.parse_msg(msg)

    expected_device_data = {
        "mqtt_id": "1",
        "device_type_name": "device_type_name",
        "remote_name": "remote_name - 1",
    }

    assert device_data == expected_device_data


def test_parse_msg_extra_values():
    duplex_messenger = BaseDuplexMessenger()

    msg = "1,device_type_name,remote_name - 1,EXTRAS"
    _, extras = duplex_messenger.parse_msg(msg)

    assert next(extras) == "EXTRAS"


def test_parse_msg_short_messages_raise_stop_iteration():
    duplex_messenger = BaseDuplexMessenger()

    short_msg = "1"
    with pytest.raises(StopIteration):
        duplex_messenger.parse_msg(short_msg)

    short_msg = "1,device_type_name"
    with pytest.raises(StopIteration):
        duplex_messenger.parse_msg(short_msg)


def test__compose_param():
    assert "&key=value" == BaseDuplexMessenger()._compose_param("key", "value")


def test_default_parse_msg():
    default_duplex_messenger = DefaultDuplexMessenger()

    msg = "1,device_type_name,remote_name - 1"
    device_data = default_duplex_messenger.parse_msg(msg)

    expected_device_data = {
        "mqtt_id": "1",
        "device_type_name": "device_type_name",
        "remote_name": "remote_name - 1",
    }

    assert device_data == expected_device_data


def test_default_parse_msg_short_messages_raise_stop_iteration():
    default_duplex_messenger = DefaultDuplexMessenger()

    short_msg = "1"
    with pytest.raises(StopIteration):
        default_duplex_messenger.parse_msg(short_msg)

    short_msg = "1,device_type_name"
    with pytest.raises(StopIteration):
        default_duplex_messenger.parse_msg(short_msg)
