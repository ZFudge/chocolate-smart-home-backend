from unittest.mock import call, patch

import pytest
from sqlalchemy.exc import NoResultFound
from paho.mqtt.client import MQTTMessage

import chocolate_smart_home.mqtt.handler as mqtt_handler


def test_device_data_received_results(empty_test_db):
    handler = mqtt_handler.MQTTMessageHandler()
    msg = MQTTMessage(b"test_topic")
    msg.payload = b"1,DEVICE_TYPE,Remote Name - unique identifier"
    device = handler.device_data_received(0, None, msg)

    assert device.client.mqtt_id == 1
    assert device.device_type.name == "DEVICE_TYPE"
    assert device.remote_name == "Remote Name - unique identifier"
    assert device.device_name.name == "Remote Name"


def test_plugin_method_calls(empty_test_db):
    msg = MQTTMessage(b"test_topic")
    msg.payload = b"1,UNKNOWN_DEVICE_TYPE,Remote Name - uid"

    with (patch("chocolate_smart_home.mqtt.handler.get_device_plugin_by_device_type") as get_plugin,
          patch("chocolate_smart_home.mqtt.handler.get_device_by_mqtt_client_id", side_effect=NoResultFound) as get_device):
        mqtt_handler.MQTTMessageHandler().device_data_received(0, None, msg)

        get_plugin.assert_called_once_with("UNKNOWN_DEVICE_TYPE")
        get_plugin.return_value["DuplexMessenger"]().parse_msg.assert_called_once_with(
            "1,UNKNOWN_DEVICE_TYPE,Remote Name - uid"
        )
        get_plugin.return_value["DeviceManager"]().create_device.assert_called_once_with(
            get_plugin.return_value["DuplexMessenger"]().parse_msg.return_value
        )
        get_device.assert_called_once_with("1")

        get_device.side_effect = lambda *x: None
        mqtt_handler.MQTTMessageHandler().device_data_received(0, None, msg)

        assert get_plugin.return_value["DuplexMessenger"]().parse_msg.call_args_list == [
            call("1,UNKNOWN_DEVICE_TYPE,Remote Name - uid"),
            call("1,UNKNOWN_DEVICE_TYPE,Remote Name - uid"),
        ]
        get_plugin.return_value["DeviceManager"]().update_device.assert_called_with(
            get_plugin.return_value["DuplexMessenger"]().parse_msg.return_value
        )

        mqtt_handler.MQTTMessageHandler().device_data_received(0, None, msg)

        assert get_plugin.return_value["DuplexMessenger"]().parse_msg.call_args_list == [
            call("1,UNKNOWN_DEVICE_TYPE,Remote Name - uid"),
            call("1,UNKNOWN_DEVICE_TYPE,Remote Name - uid"),
            call("1,UNKNOWN_DEVICE_TYPE,Remote Name - uid"),
        ]
        get_plugin.return_value["DeviceManager"]().update_device.assert_called_with(
            get_plugin.return_value["DuplexMessenger"]().parse_msg.return_value
        )


def test_empty_payload():
    msg = MQTTMessage(b"test_topic")
    msg.payload = None

    with (patch("chocolate_smart_home.mqtt.handler.get_device_plugin_by_device_type") as get_plugin,
          patch("chocolate_smart_home.mqtt.handler.get_device_by_mqtt_client_id", side_effect=NoResultFound) as get_device):
        mqtt_handler.MQTTMessageHandler().device_data_received(0, None, msg)
        get_plugin.assert_not_called()
        get_device.assert_not_called()


def test_too_short_msg_raises_stop_iteration(empty_test_db):
    msg = MQTTMessage(b"test_topic")
    msg.payload = b"1,DEVICE_TYPE"
    expected_exc_text = "Not enough comma-separated values in message.payload. payload='1,DEVICE_TYPE'."

    with pytest.raises(StopIteration, match=expected_exc_text):
        mqtt_handler.MQTTMessageHandler().device_data_received(0, None, msg)

