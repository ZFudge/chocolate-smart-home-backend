from unittest.mock import patch

from paho.mqtt.client import MQTTMessage

from src.mqtt.handler import mqtt_message_handler


def test_valid_payload_mqtt_message_handler():
    message = MQTTMessage()
    message.payload = b"1,test_device_type_name"
    with patch("src.mqtt.handler.get_device_by_id") as get_device_by_id:
        mqtt_message_handler(None, None, message)
        get_device_by_id.assert_called_once_with(1)


def test_none_payload_mqtt_message_handler():
    message = MQTTMessage()
    message.payload = None
    with patch("src.mqtt.handler.get_device_by_id") as get_device_by_id:
        mqtt_message_handler(None, None, message)
        get_device_by_id.assert_not_called()


def test_invalid_payload_mqtt_message_handler():
    message = MQTTMessage()
    message.payload = b"invalid"
    with patch("src.mqtt.handler.get_device_by_id") as get_device_by_id, patch(
        "src.mqtt.handler.logger.error"
    ) as mock_logger:
        mqtt_message_handler(None, None, message)
        get_device_by_id.assert_not_called()
        mock_logger.assert_called_once_with('Received invalid payload: "invalid"')
