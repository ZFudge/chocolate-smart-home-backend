import pytest
from paho.mqtt.client import MQTTMessage

from chocolate_smart_home.mqtt.handler import MQTTMessageHandler


def test_turn_off_message(populated_test_db):
    """Turn off, on, and off again, validating the returned device's .on
    attribute value each time."""
    message = MQTTMessage(b"test_topic")
    message.payload = b"123,on_off,Remote Name - uid,0"

    on_off_device = MQTTMessageHandler().device_data_received(0, None, message)
    device = on_off_device.device

    assert device.id == 1
    assert device.device_type.name == "on_off"
    assert device.device_name.name == "Remote Name"
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
    assert device.device_name.name == "Remote Name"
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

    with pytest.raises(StopIteration) as e:
        MQTTMessageHandler().device_data_received(0, None, message)
