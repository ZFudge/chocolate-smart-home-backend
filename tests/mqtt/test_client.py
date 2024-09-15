from unittest.mock import Mock

import pytest
from paho.mqtt import MQTTException
from paho.mqtt.client import MQTT_ERR_SUCCESS

from chocolate_smart_home.mqtt.client import MQTTClient


@pytest.fixture
def mqtt_client_unconnected():
    mqtt_client = MQTTClient(host="127.0.0.1")
    mqtt_client._client = Mock()
    mqtt_client._client.publish.return_value = (MQTT_ERR_SUCCESS, None)
    yield mqtt_client


@pytest.fixture
def mqtt_client():
    mqtt_client = MQTTClient(host="127.0.0.1")
    mqtt_client._client = Mock()
    mqtt_client._client.publish.return_value = (MQTT_ERR_SUCCESS, None)
    mqtt_client.connect()
    yield mqtt_client


def test_client_connect(mqtt_client_unconnected):
    mqtt_client = mqtt_client_unconnected
    _client = mqtt_client._client

    assert _client.connect.call_count == 0

    mqtt_client.connect()

    mqtt_client._client.connect.assert_called()
    mqtt_client._client.loop_start.assert_called()
    mqtt_client._client.message_callback_add.assert_called()
    mqtt_client._client.subscribe.assert_called()


def test_client_publish(mqtt_client):
    TEST_TOPIC = "TEST_TOPIC"
    TEST_MESSAGE = ""
    mqtt_client.publish(topic=TEST_TOPIC, message=TEST_MESSAGE)
    mqtt_client._client.publish.assert_called_once_with(TEST_TOPIC, TEST_MESSAGE)


def test_client_disconnect(mqtt_client):
    mqtt_client.disconnect()
    mqtt_client._client.disconnect.assert_called()


def test_client_publish_fail():
    mqtt_client = MQTTClient(host="127.0.0.1")
    mqtt_client._client = Mock()
    mqtt_client._client.publish.return_value = (None, None)

    mqtt_client.connect()
    callback = Mock()
    with pytest.raises(MQTTException, match="Failed!"):
        mqtt_client.publish(topic="TEST_TOPIC", message="TEST_MESSAGE", callback=callback)
    callback.assert_called_once()


def test_client_request_all_devices_data(mqtt_client):
    mqtt_client.request_all_devices_data()
    mqtt_client._client.publish.assert_called_once_with("/broadcast_request_devices_state/", "")
