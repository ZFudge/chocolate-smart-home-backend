from unittest.mock import Mock

from paho.mqtt.client import MQTT_ERR_SUCCESS
import pytest

from chocolate_smart_home.mqtt.client import MQTTClient


@pytest.fixture
def mqtt_client():
    mqtt_client = MQTTClient(host="127.0.0.1")
    mqtt_client._client = Mock()
    mqtt_client._client.publish.return_value = (MQTT_ERR_SUCCESS, None)
    yield mqtt_client


def test_client_connect(mqtt_client):
    _client = mqtt_client._client

    assert _client.connect.call_count == 0

    mqtt_client.connect()

    mqtt_client._client.connect.assert_called()
    mqtt_client._client.loop_start.assert_called()
    mqtt_client._client.message_callback_add.assert_called()
    mqtt_client._client.subscribe.assert_called()


def test_client_publish(mqtt_client):
    _client = mqtt_client._client
    mqtt_client.connect()

    TEST_TOPIC = "TEST_TOPIC"
    TEST_MESSAGE = ""
    mqtt_client.publish(topic=TEST_TOPIC, message=TEST_MESSAGE)

    mqtt_client._client.publish.assert_called_once_with(TEST_TOPIC, TEST_MESSAGE)


def test_client_disconnect(mqtt_client):
    _client = mqtt_client._client
    mqtt_client.connect()
    mqtt_client.disconnect()

    mqtt_client._client.disconnect.assert_called()


def test_client_publish_fail():
    mqtt_client = MQTTClient(host="127.0.0.1")
    mqtt_client._client = Mock()
    mqtt_client._client.publish.return_value = (None, None)

    mqtt_client.connect()
    callback = Mock()
    mqtt_client.publish(topic="TEST_TOPIC", message="TEST_MESSAGE", callback=callback)

    callback.assert_called_once()
