from paho.mqtt.client import MQTTMessage
import pytest

import chocolate_smart_home.mqtt.handlers as handlers


def test_base_message(test_database):
    message = MQTTMessage(b'test_topic')
    message.payload = b"1,DEVICE_TYPE,Remote Name - unique identifier"
    device = handlers.device_data_received(0, None, message)

    assert device.mqtt_id == 1
    assert device.device_type.name == "DEVICE_TYPE"
    assert device.remote_name == "Remote Name - unique identifier"
    assert device.name == "Remote Name"
