from typing import Iterable

import pytest

from src.models import (
    Device as DeviceModel,
    DeviceType as DeviceTypeModel,
)
from src.plugins.BaseControllerToServerMessenger import (
    BaseControllerToServerMessenger,
    DefaultControllerToServerMessenger,
)
from src.schemas import (
    DeviceFrontend as DeviceFrontendSchema,
    DeviceReceived as DeviceReceivedSchema,
)


def test_DefaultControllerToServerMessenger_parse_controller_msg():
    assert DefaultControllerToServerMessenger().parse_controller_msg(
        "123,test_device_type_name,test_remote_name"
    ) == DeviceReceivedSchema(
        mqtt_id=123,
        device_type_name="test_device_type_name",
        remote_name="test_remote_name",
        name="test_remote_name",
    )


def test_BaseControllerToServerMessenger_parse_controller_msg():
    device, msg_seq = BaseControllerToServerMessenger().parse_controller_msg(
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


def test_BaseControllerToServerMessenger_StopIteration_raised_when_not_enough_values_in_payload_for_base_duplex_messenger_parse_controller_msg():
    with pytest.raises(StopIteration):
        BaseControllerToServerMessenger().parse_controller_msg(
            "123,test_device_type_name"
        )


def test_BaseControllerToServerMessenger_StopIteration_raised_when_not_enough_values_in_payload_for_default_duplex_messenger_parse_controller_msg():
    with pytest.raises(StopIteration):
        BaseControllerToServerMessenger().parse_controller_msg(
            "123,test_device_type_name"
        )


def test_BaseControllerToServerMessenger_get_device_frontend():
    assert BaseControllerToServerMessenger().get_device_frontend(
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
