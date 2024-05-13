from unittest.mock import Mock

import pytest
from paho.mqtt.client import MQTTMessage

import chocolate_smart_home.crud as crud
from chocolate_smart_home.mqtt.handler import MQTTMessageHandler


def test_device_data_received_results(test_database):
    handler = MQTTMessageHandler()
    message = MQTTMessage(b'test_topic')
    message.payload = b"1,DEVICE_TYPE,Remote Name - unique identifier"
    device = handler.device_data_received(0, None, message)

    assert device.mqtt_id == 1
    assert device.device_type.name == "DEVICE_TYPE"
    assert device.remote_name == "Remote Name - unique identifier"
    assert device.name == "Remote Name"


def test_method_calls(test_database):
    pass
