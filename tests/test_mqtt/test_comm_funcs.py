from unittest.mock import Mock, call

from src.pubsub.comm_funcs import (
    publish,
    publish_all,
    subscribe,
    subscribe_all,
    request_all_devices_data,
)


def test_comm_funcs_publish_all_calls_mqtt_client_publish(mqtt_client):
    publish_all(
        topics=["test_topic_a", "test_topic_b", "test_topic_c"], message="test_message"
    )
    mqtt_client.publish.assert_has_calls(
        [
            call("test_topic_a", "test_message"),
            call("test_topic_b", "test_message"),
            call("test_topic_c", "test_message"),
        ]
    )


def test_comm_funcs_publish_calls_mqtt_client_publish(mqtt_client):
    publish(topic="test_topic", message="test_message")
    mqtt_client.publish.assert_called_once_with("test_topic", "test_message")


def test_comm_funcs_request_all_devices_data_calls_publish(mqtt_client):
    request_all_devices_data()
    mqtt_client.publish.assert_called_once_with("/broadcast_request_devices_state/", "")


def test_comm_funcs_subscribe_calls_mqtt_client_subscribe(mqtt_client):
    handler = Mock()
    subscribe(topic="test_topic", handler=handler)
    mqtt_client.subscribe.assert_called_once_with(topic="test_topic")


def test_comm_funcs_subscribe_all_calls_mqtt_client_subscribe(mqtt_client):
    handler = Mock()
    subscribe_all(
        topics=["test_topic_a", "test_topic_b", "test_topic_c"], handler=handler
    )
    mqtt_client.subscribe.assert_has_calls(
        [
            call(topic="test_topic_a"),
            call(topic="test_topic_b"),
            call(topic="test_topic_c"),
        ]
    )


def test_comm_funcs_subscribe_all_calls_mqtt_client_message_callback_add(mqtt_client):
    handler = Mock()
    subscribe_all(
        topics=["test_topic_a", "test_topic_b", "test_topic_c"], handler=handler
    )
    mqtt_client.message_callback_add.assert_has_calls(
        [
            call(sub="test_topic_a", callback=handler),
            call(sub="test_topic_b", callback=handler),
            call(sub="test_topic_c", callback=handler),
        ]
    )


def test_comm_funcs_subscribe_calls_mqtt_client_message_callback_add(mqtt_client):
    handler = Mock()
    subscribe(topic="test_topic", handler=handler)
    mqtt_client.message_callback_add.assert_called_once_with(
        sub="test_topic", callback=handler
    )
