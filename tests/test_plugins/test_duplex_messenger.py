from typing import Iterable

import pytest

from src.models import (
    Device as DeviceModel,
    DeviceType as DeviceTypeModel,
)
from src.plugins.base_duplex_messenger import (
    DefaultDuplexMessenger,
    IncomingMessenger,
    OutgoingMessenger,
)
from src.schemas import (
    DeviceFrontend as DeviceFrontendSchema,
    DeviceReceived as DeviceReceivedSchema,
    WebsocketMessage as WebsocketMessageSchema,
)


def test_DefaultDuplexMessenger_parse_msg():
    assert DefaultDuplexMessenger().parse_msg(
        "123,test_device_type_name,test_remote_name"
    ) == DeviceReceivedSchema(
        mqtt_id=123,
        device_type_name="test_device_type_name",
        remote_name="test_remote_name",
        name="test_remote_name",
    )


def test_IncomingMessenger_parse_msg():
    device, msg_seq = IncomingMessenger().parse_msg(
        "123,test_device_type_name,test_remote_name"
    )
    assert device == DeviceReceivedSchema(
        mqtt_id=123,
        device_type_name="test_device_type_name",
        remote_name="test_remote_name",
        name="test_remote_name",
    )
    assert isinstance(msg_seq, Iterable)
    with pytest.raises(StopIteration):
        next(msg_seq)


def test_IncomingMessenger_StopIteration_raised_when_not_enough_values_in_payload_for_base_duplex_messenger_parse_msg():
    with pytest.raises(StopIteration):
        IncomingMessenger().parse_msg("123,test_device_type_name")


def test_IncomingMessenger_StopIteration_raised_when_not_enough_values_in_payload_for_default_duplex_messenger_parse_msg():
    with pytest.raises(StopIteration):
        IncomingMessenger().parse_msg("123,test_device_type_name")


def test_IncomingMessenger_compose_msg_returns_input():
    assert IncomingMessenger().compose_msg("123") == "123"


def test_IncomingMessenger_compose_msg_handles_arbitrary_args_and_kwargs():
    IncomingMessenger().compose_msg("123", 0, True, a=1, b=2, c=3)


def test_IncomingMessenger__compose_param():
    assert IncomingMessenger()._compose_param("k", 0) == "&k=0"


def test_BaseDuplexMessenger_get_topics():
    assert list(
        IncomingMessenger().get_topics(
            WebsocketMessageSchema(
                device_type_name="test_device_type_name",
                name="test_name",
                value=0,
                mqtt_ids=[123],
            )
        )
    ) == ["/test_device_type_name/123/"]


def test_OutgoingMessenger_get_device_frontend():
    assert OutgoingMessenger().get_device_frontend(
        DeviceModel(
            device_type=DeviceTypeModel(id=1, name="test_device_type_name"),
            last_seen=None,
            last_update_sent=None,
            mqtt_id=123,
            name="test_remote_name",
            reboots=0,
            remote_name="test_remote_name",
            tags=[],
        )
    ) == DeviceFrontendSchema(
        device_type_name="test_device_type_name",
        last_seen=None,
        last_update_sent=None,
        mqtt_id=123,
        name="test_remote_name",
        reboots=0,
        remote_name="test_remote_name",
        tags=None,
    )
