from unittest.mock import patch

from sqlalchemy.exc import NoResultFound
from paho.mqtt.client import MQTTMessage

import chocolate_smart_home.mqtt.handler as mqtt_handler


def test_device_data_received_results(test_database):
    handler = mqtt_handler.MQTTMessageHandler()
    msg = MQTTMessage(b'test_topic')
    msg.payload = b"1,DEVICE_TYPE,Remote Name - unique identifier"
    device = handler.device_data_received(0, None, msg)

    assert device.mqtt_id == 1
    assert device.device_type.name == "DEVICE_TYPE"
    assert device.remote_name == "Remote Name - unique identifier"
    assert device.name == "Remote Name"


def test_plugin_method_calls(test_database):
    msg = MQTTMessage(b'test_topic')
    msg.payload = b"1,UNKNOWN_DEVICE_TYPE,Remote Name - uid"

    with (patch('chocolate_smart_home.mqtt.handler.get_device_plugin_by_device_type') as get_plugin,
          patch('chocolate_smart_home.mqtt.handler.get_device_by_mqtt_id', side_effect=NoResultFound) as get_device):
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

        get_plugin.return_value["DuplexMessenger"]().parse_msg.call_args_list == [
            "1,UNKNOWN_DEVICE_TYPE,Remote Name - uid",
            "1,UNKNOWN_DEVICE_TYPE,Remote Name - uid",
        ]
        get_plugin.return_value["DeviceManager"]().update_device.assert_called_with(
            get_plugin.return_value["DuplexMessenger"]().parse_msg.return_value
        )

        mqtt_handler.MQTTMessageHandler().device_data_received(0, None, msg)

        get_plugin.return_value["DuplexMessenger"]().parse_msg.call_args_list == [
            "1,UNKNOWN_DEVICE_TYPE,Remote Name - uid",
            "1,UNKNOWN_DEVICE_TYPE,Remote Name - uid",
            "1,UNKNOWN_DEVICE_TYPE,Remote Name - uid",
        ]
        get_plugin.return_value["DeviceManager"]().update_device.assert_called_with(
            get_plugin.return_value["DuplexMessenger"]().parse_msg.return_value
        )
