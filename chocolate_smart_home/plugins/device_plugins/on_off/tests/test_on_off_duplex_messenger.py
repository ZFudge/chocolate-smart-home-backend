import pytest
from paho.mqtt.client import MQTTMessage

from chocolate_smart_home.mqtt.handler import MQTTMessageHandler
from chocolate_smart_home.plugins.device_plugins.on_off.duplex_messenger import (
    OnOffDuplexMessenger,
)
from chocolate_smart_home.plugins.device_plugins.on_off.schemas import (
    OnOffDeviceReceived,
)
from chocolate_smart_home.schemas.device import DeviceReceived


def test_turn_off_message(populated_test_db):
    """Turn off, on, and off again, validating the returned device's .on
    attribute value each time."""
    message = MQTTMessage(b"test_topic")
    message.payload = b"123,on_off,Remote Name - uid,0"

    on_off_device = MQTTMessageHandler().device_data_received(0, None, message)
    device = on_off_device.device

    assert device.id == 1
    assert device.device_type.name == "on_off"
    assert device.name == "Remote Name"
    assert on_off_device.on is False

    message.payload = b"123,on_off,Remote Name - uid,1"
    on_off_device = MQTTMessageHandler().device_data_received(0, None, message)
    assert on_off_device.on is True
    assert on_off_device.device is device

    message.payload = b"123,on_off,Remote Name - uid,0"
    on_off_device = MQTTMessageHandler().device_data_received(0, None, message)
    assert on_off_device.on is False
    assert on_off_device.device is device


def test_turn_on_message(populated_test_db):
    """Turn on, off, and on again, validating the returned device's .on
    attribute value each time."""
    message = MQTTMessage(b"test_topic")
    message.payload = b"456,on_off,Remote Name - uid,1"

    on_off_device = MQTTMessageHandler().device_data_received(0, None, message)
    device = on_off_device.device

    assert device.id == 2
    assert device.device_type.name == "on_off"
    assert device.name == "Remote Name"
    assert on_off_device.on is True

    message.payload = b"456,on_off,Remote Name - uid,0"
    on_off_device = MQTTMessageHandler().device_data_received(0, None, message)
    assert on_off_device.on is False

    message.payload = b"456,on_off,Remote Name - uid,1"
    on_off_device = MQTTMessageHandler().device_data_received(0, None, message)
    assert on_off_device.on is True


def test_message_handler_fails_on_missing_values(populated_test_db):
    """Assert failure when message payload has too few comma-separated values
    for the plugin message handler's .parse_msg method."""
    message = MQTTMessage(b"test_topic")
    message.payload = b"111,on_off,Remote Name40 - uid"

    with pytest.raises(StopIteration):
        MQTTMessageHandler().device_data_received(0, None, message)


def test_on_off_serialize():
    message = MQTTMessage(b"test_topic")
    message.payload = b"123,on_off,Remote Name - uid,1"

    expected_serialized_data_dict = {
        "on": True,
        "mqtt_id": 123,
        "device_type_name": "on_off",
        "remote_name": "Remote Name - uid",
    }

    on_off_device_data = OnOffDeviceReceived(
        on=True,
        device=DeviceReceived(
            mqtt_id=123,
            device_type_name="on_off",
            remote_name="Remote Name - uid",
        ),
    )
    serialized_data = OnOffDuplexMessenger().serialize(on_off_device_data)

    assert serialized_data == expected_serialized_data_dict
