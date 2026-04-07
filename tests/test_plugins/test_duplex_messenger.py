from typing import Iterable

import pytest

from src.plugins.base_duplex_messenger import (
    BaseDuplexMessenger,
    DefaultDuplexMessenger,
)
from src.schemas.device import DeviceReceived


def test_base_duplex_messenger_parse_msg():
    device, msg_seq = BaseDuplexMessenger().parse_msg(
        "123,test_device_type_name,test_remote_name"
    )
    assert device == DeviceReceived(
        mqtt_id=123,
        device_type_name="test_device_type_name",
        remote_name="test_remote_name",
        name="test_remote_name",
    )
    assert isinstance(msg_seq, Iterable)
    with pytest.raises(StopIteration):
        next(msg_seq)


def test_default_duplex_messenger_parse_msg():
    assert DefaultDuplexMessenger().parse_msg(
        "123,test_device_type_name,test_remote_name"
    ) == DeviceReceived(
        mqtt_id=123,
        device_type_name="test_device_type_name",
        remote_name="test_remote_name",
        name="test_remote_name",
    )


def test_StopIteration_raised_when_not_enough_values_in_payload_for_base_duplex_messenger_parse_msg():
    with pytest.raises(StopIteration):
        BaseDuplexMessenger().parse_msg("123,test_device_type_name")


def test_StopIteration_raised_when_not_enough_values_in_payload_for_default_duplex_messenger_parse_msg():
    with pytest.raises(StopIteration):
        DefaultDuplexMessenger().parse_msg("123,test_device_type_name")
