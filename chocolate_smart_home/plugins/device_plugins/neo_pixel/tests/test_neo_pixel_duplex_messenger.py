import pytest
from paho.mqtt.client import MQTTMessage

from chocolate_smart_home.mqtt.handler import MQTTMessageHandler


def test_turn_off_message(populated_test_db):
    """Turn off, on, and off again, validating the returned device's .on
    attribute value each time."""
    message = MQTTMessage(b"test_topic")
    message.payload = b"123,neo_pixel,Remote Name - uid,0,5,255"

    neo_pixel_device = MQTTMessageHandler().device_data_received(0, None, message)
    device = neo_pixel_device.device

    assert device.id == 1
    assert device.device_type.name == "neo_pixel"
    assert device.device_name.name == "Remote Name"
    assert neo_pixel_device.on is False

    message.payload = b"123,neo_pixel,Remote Name - uid,1,5,255"
    neo_pixel_device = MQTTMessageHandler().device_data_received(0, None, message)
    assert neo_pixel_device.on is True
    assert neo_pixel_device.device is device

    message.payload = b"123,neo_pixel,Remote Name - uid,0,5,255"
    neo_pixel_device = MQTTMessageHandler().device_data_received(0, None, message)
    assert neo_pixel_device.on is False
    assert neo_pixel_device.device is device


def test_turn_on_message(populated_test_db):
    """Turn on, off, and on again, validating the returned device's .on
    attribute value each time."""
    message = MQTTMessage(b"test_topic")
    message.payload = b"456,neo_pixel,Remote Name - uid,1,5,255"

    neo_pixel_device = MQTTMessageHandler().device_data_received(0, None, message)
    device = neo_pixel_device.device

    assert device.id == 2
    assert device.device_type.name == "neo_pixel"
    assert device.device_name.name == "Remote Name"
    assert neo_pixel_device.on is True

    message.payload = b"456,neo_pixel,Remote Name - uid,0,5,255"
    neo_pixel_device = MQTTMessageHandler().device_data_received(0, None, message)
    assert neo_pixel_device.on is False

    message.payload = b"456,neo_pixel,Remote Name - uid,1,5,255"
    neo_pixel_device = MQTTMessageHandler().device_data_received(0, None, message)
    assert neo_pixel_device.on is True


def test_message_handler_fails_on_missing_values(populated_test_db):
    """Assert failure when message payload has too few comma-separated values
    for the plugin message handler's .parse_msg method."""
    message = MQTTMessage(b"test_topic")
    message.payload = b"111,neo_pixel,Remote Name40 - uid"

    with pytest.raises(StopIteration):
        MQTTMessageHandler().device_data_received(0, None, message)
