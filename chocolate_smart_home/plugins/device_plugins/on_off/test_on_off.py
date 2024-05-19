from paho.mqtt.client import MQTTMessage

from chocolate_smart_home.mqtt.handler import MQTTMessageHandler


def test_msg_handler(test_database):
    handler = MQTTMessageHandler()
    message = MQTTMessage(b'test_topic')
    message.payload = b"1,ON_OFF,Remote Name - uid,0"
    device = handler.device_data_received(0, None, message)

    assert device.on is False
