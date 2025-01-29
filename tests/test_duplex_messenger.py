import pytest

from chocolate_smart_home.plugins.base_duplex_messenger import (
    BaseDuplexMessenger,
    DefaultDuplexMessenger,
)
from chocolate_smart_home.schemas import DeviceReceived, WebsocketMessage


def test_parse_msg():
    msg = "1,device_type_name,remote_name - 1"
    device_data, _ = BaseDuplexMessenger().parse_msg(msg)
    expected_device_data = DeviceReceived(
        mqtt_id=1,
        device_type_name="device_type_name",
        remote_name="remote_name - 1",
    )
    assert device_data == expected_device_data


def test_parse_msg_extra_values():
    msg = "1,device_type_name,remote_name - 1,EXTRAS"
    _, extras = BaseDuplexMessenger().parse_msg(msg)
    assert next(extras) == "EXTRAS"


def test_parse_msg_short_messages_raise_stop_iteration():
    short_msg = "1"
    expected_exc_text = (
        "Not enough comma-separated values in message.payload. payload='1'."
    )
    with pytest.raises(StopIteration, match=expected_exc_text):
        BaseDuplexMessenger().parse_msg(short_msg)

    short_msg = "1,device_type_name"
    expected_exc_text = "Not enough comma-separated values in message.payload. payload='1,device_type_name'."
    with pytest.raises(StopIteration, match=expected_exc_text):
        BaseDuplexMessenger().parse_msg(short_msg)


def test__compose_param():
    assert "&key=value" == BaseDuplexMessenger()._compose_param("key", "value")


def test_default_parse_msg():
    default_duplex_messenger = DefaultDuplexMessenger()
    msg = "1,device_type_name,remote_name - 1"
    device_data = default_duplex_messenger.parse_msg(msg)

    expected_device_data = DeviceReceived(
        mqtt_id="1",
        device_type_name="device_type_name",
        remote_name="remote_name - 1",
    )
    assert device_data == expected_device_data


def test_default_parse_msg_short_messages_raise_stop_iteration():
    default_duplex_messenger = DefaultDuplexMessenger()

    empty_msg = ""
    expected_exc_text = (
        "Not enough comma-separated values in message.payload. payload=''."
    )
    with pytest.raises(StopIteration, match=expected_exc_text):
        default_duplex_messenger.parse_msg(empty_msg)

    short_msg = "1"
    expected_exc_text = (
        "Not enough comma-separated values in message.payload. payload='1'."
    )
    with pytest.raises(StopIteration, match=expected_exc_text):
        default_duplex_messenger.parse_msg(short_msg)

    short_msg = "1,device_type_name"
    expected_exc_text = "Not enough comma-separated values in message.payload. payload='1,device_type_name'."
    with pytest.raises(StopIteration, match=expected_exc_text):
        default_duplex_messenger.parse_msg(short_msg)


def test_get_topics():
    """Test that get_topics returns a list of topics when using any combination of the following keys of type int or list[int]:
    - id
    - ids
    - mqtt_id
    - mqtt_ids
    """
    device_template = {
        "device_type_name": "TEST_DEVICE_TYPE_NAME",
        "name": "Property Name",
        "value": "Property Value",
    }

    device_data = WebsocketMessage(id=123, **device_template)
    topics = BaseDuplexMessenger().get_topics(ws_msg=device_data)
    assert list(topics) == ["/TEST_DEVICE_TYPE_NAME/123/"]

    device_data = WebsocketMessage(ids=456, **device_template)
    topics = BaseDuplexMessenger().get_topics(ws_msg=device_data)
    assert list(topics) == ["/TEST_DEVICE_TYPE_NAME/456/"]

    device_data = WebsocketMessage(mqtt_id=789, **device_template)
    topics = BaseDuplexMessenger().get_topics(ws_msg=device_data)
    assert list(topics) == ["/TEST_DEVICE_TYPE_NAME/789/"]

    device_data = WebsocketMessage(mqtt_ids=123, **device_template)
    topics = BaseDuplexMessenger().get_topics(ws_msg=device_data)
    assert list(topics) == ["/TEST_DEVICE_TYPE_NAME/123/"]

    device_data = WebsocketMessage(id=[456], **device_template)
    topics = BaseDuplexMessenger().get_topics(ws_msg=device_data)
    assert list(topics) == ["/TEST_DEVICE_TYPE_NAME/456/"]

    device_data = WebsocketMessage(ids=[456], **device_template)
    topics = BaseDuplexMessenger().get_topics(ws_msg=device_data)
    assert list(topics) == ["/TEST_DEVICE_TYPE_NAME/456/"]

    device_data = WebsocketMessage(mqtt_id=[456], **device_template)
    topics = BaseDuplexMessenger().get_topics(ws_msg=device_data)
    assert list(topics) == ["/TEST_DEVICE_TYPE_NAME/456/"]

    device_data = WebsocketMessage(mqtt_ids=[456, 789], **device_template)
    topics = BaseDuplexMessenger().get_topics(ws_msg=device_data)
    assert list(topics) == [
        "/TEST_DEVICE_TYPE_NAME/456/",
        "/TEST_DEVICE_TYPE_NAME/789/",
    ]
