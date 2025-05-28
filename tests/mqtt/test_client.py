from unittest.mock import Mock

import pytest
from paho.mqtt import MQTTException
from paho.mqtt.client import MQTT_ERR_SUCCESS

from src.mqtt.client import MQTTClient


@pytest.fixture
def mqtt_client():
    mqtt_client = MQTTClient(host="127.0.0.1")
    mqtt_client._client = Mock()
    mqtt_client._client.publish.return_value = (MQTT_ERR_SUCCESS, None)
    mqtt_client.connect()
    yield mqtt_client


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
        mqtt_client.publish(
            topic="TEST_TOPIC", message="TEST_MESSAGE", callback=callback
        )
    callback.assert_called_once()


def test_client_request_all_devices_data(mqtt_client):
    mqtt_client.request_all_devices_data()
    mqtt_client._client.publish.assert_called_once_with(
        "/broadcast_request_devices_state/", ""
    )
