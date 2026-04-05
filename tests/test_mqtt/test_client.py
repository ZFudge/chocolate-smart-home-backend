from unittest.mock import Mock, call

import pytest
from paho.mqtt import MQTTException
from paho.mqtt.client import MQTT_ERR_SUCCESS, MQTT_ERR_ERRNO

from src.mqtt.context import get_mqtt_client


def test_mqtt_client_connect():
    mqtt_client = get_mqtt_client(host="127.0.0.1")
    mqtt_client._client.connect = Mock()
    mqtt_client._client.loop_start = Mock()
    mqtt_client.subscribe_all = Mock()
    mqtt_client.connect()
    mqtt_client._client.connect.assert_called_once_with(
        mqtt_client._host, mqtt_client._port, 60
    )
    mqtt_client._client.loop_start.assert_called_once()
    mqtt_client.subscribe_all.assert_called_once()


def test_mqtt_client_duplicate_connect_call(mqtt_client):
    mqtt_client._client.connect = Mock()
    mqtt_client.connect()
    mqtt_client._client.connect.assert_not_called()


def test_mqtt_client_is_connected(mqtt_client):
    assert mqtt_client.is_connected()


def test_mqtt_client_disconnect(mqtt_client):
    mqtt_client._client.disconnect = Mock()
    mqtt_client.disconnect()
    mqtt_client._client.disconnect.assert_called()


def test_mqtt_client__publish(mqtt_client):
    TEST_TOPIC = "TEST_TOPIC"
    TEST_MESSAGE = ""
    mqtt_client.publish(topic=TEST_TOPIC, message=TEST_MESSAGE)
    mqtt_client._client.publish.assert_called_once_with(
        topic=TEST_TOPIC, message=TEST_MESSAGE
    )


def test_failed_mqtt_publish(mqtt_client):
    mqtt_client._client.publish.return_value = (MQTT_ERR_ERRNO, None)
    with pytest.raises(
        MQTTException,
        match=f"Failed! : TEST_MESSAGE rc_update: {MQTT_ERR_ERRNO} message_id_update: None",
    ):
        mqtt_client.publish(topic="TEST_TOPIC", message="TEST_MESSAGE")


def test_mqtt_client_publish_all(mqtt_client):
    mqtt_client._client.publish = Mock()
    mqtt_client._client.publish.return_value = (MQTT_ERR_SUCCESS, None)
    mqtt_client.publish_all(
        topics=["TEST_TOPIC_1", "TEST_TOPIC_2"], message="TEST_MESSAGE"
    )
    mqtt_client._client.publish.assert_has_calls(
        [
            call(topic="TEST_TOPIC_1", message="TEST_MESSAGE"),
            call(topic="TEST_TOPIC_2", message="TEST_MESSAGE"),
        ]
    )


def test_mqtt_client_subscribe(mqtt_client):
    mqtt_client._client.subscribe = Mock()
    mqtt_client._client.message_callback_add = Mock()
    handler = Mock()
    mqtt_client.subscribe(topic="TEST_TOPIC", handler=handler)
    mqtt_client._client.subscribe.assert_called_once_with(topic="TEST_TOPIC")
    mqtt_client._client.message_callback_add.assert_called_once_with(
        sub="TEST_TOPIC", callback=handler
    )


def test_mqtt_client_subscribe_all(mqtt_client):
    mqtt_client.subscription_topics = ["TEST_TOPIC_1", "TEST_TOPIC_2"]
    mqtt_client.message_handler = Mock()
    mqtt_client._client.subscribe = Mock()
    mqtt_client._client.message_callback_add = Mock()
    mqtt_client.subscribe_all()
    mqtt_client._client.subscribe.assert_has_calls(
        [call(topic="TEST_TOPIC_1"), call(topic="TEST_TOPIC_2")]
    )
    mqtt_client._client.message_callback_add.assert_has_calls(
        [
            call(sub="TEST_TOPIC_1", callback=mqtt_client.message_handler),
            call(sub="TEST_TOPIC_2", callback=mqtt_client.message_handler),
        ]
    )


def test_mqtt_client_request_all_devices_data(mqtt_client):
    mqtt_client._client.publish = Mock(return_value=(MQTT_ERR_SUCCESS, None))
    mqtt_client.request_all_devices_data()
    mqtt_client._client.publish.assert_called_once_with(
        topic="/broadcast_request_devices_state/", message=""
    )
