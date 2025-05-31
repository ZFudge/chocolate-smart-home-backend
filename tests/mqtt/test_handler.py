import logging
from unittest.mock import call, patch

from sqlalchemy.exc import NoResultFound
from paho.mqtt.client import MQTTMessage

import src.mqtt.handler as mqtt_handler


LOGGER = logging.getLogger(__name__)


def test_device_data_received_results(empty_test_db):
    handler = mqtt_handler.MQTTMessageHandler()
    msg = MQTTMessage(b"test_topic")
    msg.payload = b"1,DEVICE_TYPE,Remote Name - unique identifier"
    device = handler.device_data_received(0, None, msg)

    assert device.mqtt_id == 1
    assert device.device_type.name == "DEVICE_TYPE"
    assert device.remote_name == "Remote Name - unique identifier"
    assert device.name == "Remote Name"


def test_plugin_method_calls(empty_test_db):
    msg = MQTTMessage(b"test_topic")
    msg.payload = b"1,UNKNOWN_DEVICE_TYPE,Remote Name - uid"

    with (
        patch("src.mqtt.handler.get_plugin_by_device_type") as get_plugin,
        patch(
            "src.mqtt.handler.get_device_by_mqtt_id", side_effect=NoResultFound
        ) as get_device,
    ):
        mqtt_handler.MQTTMessageHandler().device_data_received(0, None, msg)

        get_plugin.assert_called_once_with("UNKNOWN_DEVICE_TYPE")
        get_plugin.return_value["DuplexMessenger"]().parse_msg.assert_called_once_with(
            "1,UNKNOWN_DEVICE_TYPE,Remote Name - uid"
        )
        get_plugin.return_value[
            "DeviceManager"
        ]().create_device.assert_called_once_with(
            get_plugin.return_value["DuplexMessenger"]().parse_msg.return_value
        )
        get_device.assert_called_once_with("1")

        get_device.side_effect = lambda *x: None
        mqtt_handler.MQTTMessageHandler().device_data_received(0, None, msg)

        assert get_plugin.return_value[
            "DuplexMessenger"
        ]().parse_msg.call_args_list == [
            call("1,UNKNOWN_DEVICE_TYPE,Remote Name - uid"),
            call("1,UNKNOWN_DEVICE_TYPE,Remote Name - uid"),
        ]
        get_plugin.return_value["DeviceManager"]().update_device.assert_called_with(
            get_plugin.return_value["DuplexMessenger"]().parse_msg.return_value
        )

        mqtt_handler.MQTTMessageHandler().device_data_received(0, None, msg)

        assert get_plugin.return_value[
            "DuplexMessenger"
        ]().parse_msg.call_args_list == [
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

    with (
        patch("src.mqtt.handler.get_plugin_by_device_type") as get_plugin,
        patch(
            "src.mqtt.handler.get_device_by_mqtt_id", side_effect=NoResultFound
        ) as get_device,
    ):
        mqtt_handler.MQTTMessageHandler().device_data_received(0, None, msg)
        get_plugin.assert_not_called()
        get_device.assert_not_called()


def test_too_short_msg(empty_test_db, caplog):
    """Test that a message with too few comma-separated values logs an error and tolerates a StopIteration exception."""
    msg = MQTTMessage(b"test_topic")
    msg.payload = b"1,DEVICE_TYPE"
    expected_exc_text = (
        "Not enough comma-separated values in message.payload. payload='1,DEVICE_TYPE'."
    )

    caplog.set_level(logging.INFO)
    mqtt_handler.MQTTMessageHandler().device_data_received(0, None, msg)
    assert expected_exc_text in caplog.text
