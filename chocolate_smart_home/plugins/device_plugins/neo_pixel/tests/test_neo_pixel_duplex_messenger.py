import pytest
from paho.mqtt.client import MQTTMessage

from chocolate_smart_home.mqtt.handler import MQTTMessageHandler
from chocolate_smart_home.plugins.device_plugins.neo_pixel.duplex_messenger import NeoPixelDuplexMessenger
from chocolate_smart_home.plugins.device_plugins.neo_pixel.schemas import NeoPixelOptions


def test_incoming_msg_device(populated_test_db):
    message = MQTTMessage(b"test_topic")

    message.payload = b"789,neo_pixel,Remote Name - uid,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    neo_pixel_device = MQTTMessageHandler().device_data_received(0, None, message)
    device = neo_pixel_device.device

    assert device.id == 3
    assert device.device_type.name == "neo_pixel"
    assert device.device_name.name == "Remote Name"

    message.payload = b"789,neo_pixel,New Remote Name - uid,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    neo_pixel_device = MQTTMessageHandler().device_data_received(0, None, message)
    device = neo_pixel_device.device

    assert device.device_name.name == "New Remote Name"


def test_message_handler_fails_on_missing_values(populated_test_db):
    """Assert failure when message payload has too few comma-separated values for the plugin message handler's .parse_msg method."""
    message = MQTTMessage(b"test_topic")
    message.payload = b"111,neo_pixel,Remote Name40 - uid,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"

    with pytest.raises(StopIteration):
        MQTTMessageHandler().device_data_received(0, None, message)


def test_incoming_msg_on(populated_test_db):
    message = MQTTMessage(b"test_topic")

    message.payload = b"789,neo_pixel,Remote Name - uid,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    neo_pixel_device = MQTTMessageHandler().device_data_received(0, None, message)
    assert neo_pixel_device.on is True

    message.payload = b"789,neo_pixel,Remote Name - uid,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    neo_pixel_device = MQTTMessageHandler().device_data_received(0, None, message)
    assert neo_pixel_device.on is False


def test_incoming_msg_twinkle(populated_test_db):
    message = MQTTMessage(b"test_topic")

    message.payload = b"789,neo_pixel,Remote Name - uid,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    neo_pixel_device = MQTTMessageHandler().device_data_received(0, None, message)
    assert neo_pixel_device.twinkle is True

    message.payload = b"789,neo_pixel,Remote Name - uid,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    neo_pixel_device = MQTTMessageHandler().device_data_received(0, None, message)
    assert neo_pixel_device.twinkle is False


def test_incoming_msg_transform(populated_test_db):
    message = MQTTMessage(b"test_topic")

    message.payload = b"789,neo_pixel,Remote Name - uid,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    neo_pixel_device = MQTTMessageHandler().device_data_received(0, None, message)
    assert neo_pixel_device.transform is True

    message.payload = b"789,neo_pixel,Remote Name - uid,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    neo_pixel_device = MQTTMessageHandler().device_data_received(0, None, message)
    assert neo_pixel_device.transform is False


def test_incoming_msg_ms(populated_test_db):
    message = MQTTMessage(b"test_topic")

    message.payload = b"789,neo_pixel,Remote Name - uid,0,7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    neo_pixel_device = MQTTMessageHandler().device_data_received(0, None, message)
    assert neo_pixel_device.ms == 7

    message.payload = b"789,neo_pixel,Remote Name - uid,0,93,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    neo_pixel_device = MQTTMessageHandler().device_data_received(0, None, message)
    assert neo_pixel_device.ms == 93

    message.payload = b"789,neo_pixel,Remote Name - uid,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    neo_pixel_device = MQTTMessageHandler().device_data_received(0, None, message)
    assert neo_pixel_device.ms == 0


def test_incoming_msg_brightness(populated_test_db):
    message = MQTTMessage(b"test_topic")

    message.payload = b"789,neo_pixel,Remote Name - uid,0,0,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    neo_pixel_device = MQTTMessageHandler().device_data_received(0, None, message)
    assert neo_pixel_device.brightness == 255

    message.payload = b"789,neo_pixel,Remote Name - uid,0,0,110,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    neo_pixel_device = MQTTMessageHandler().device_data_received(0, None, message)
    assert neo_pixel_device.brightness == 110

    message.payload = b"789,neo_pixel,Remote Name - uid,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    neo_pixel_device = MQTTMessageHandler().device_data_received(0, None, message)
    assert neo_pixel_device.brightness == 0


def test_incoming_msg_pir_enabled(populated_test_db):
    message = MQTTMessage(b"test_topic")

    message.payload = b"789,neo_pixel,Remote Name - uid,16,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    neo_pixel_device = MQTTMessageHandler().device_data_received(0, None, message)
    assert neo_pixel_device.pir_armed is not None
    assert neo_pixel_device.pir_timeout_seconds is not None


def test_incoming_msg_pir_armed(populated_test_db):
    message = MQTTMessage(b"test_topic")

    message.payload = b"789,neo_pixel,Remote Name - uid,48,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    neo_pixel_device = MQTTMessageHandler().device_data_received(0, None, message)
    assert neo_pixel_device.pir_armed is True

    message.payload = b"789,neo_pixel,Remote Name - uid,16,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    neo_pixel_device = MQTTMessageHandler().device_data_received(0, None, message)
    assert neo_pixel_device.pir_armed is False


def test_incoming_msg_pir_timeout(populated_test_db):
    message = MQTTMessage(b"test_topic")

    message.payload = b"789,neo_pixel,Remote Name - uid,16,0,0,123,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    neo_pixel_device = MQTTMessageHandler().device_data_received(0, None, message)
    assert neo_pixel_device.pir_timeout_seconds == 123

    message.payload = b"789,neo_pixel,Remote Name - uid,16,0,0,234,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    neo_pixel_device = MQTTMessageHandler().device_data_received(0, None, message)
    assert neo_pixel_device.pir_timeout_seconds == 234

    message.payload = b"789,neo_pixel,Remote Name - uid,16,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    neo_pixel_device = MQTTMessageHandler().device_data_received(0, None, message)
    assert neo_pixel_device.pir_timeout_seconds == 0


def test_compose_msg_on():
    outgoing_msg = NeoPixelDuplexMessenger().compose_msg(NeoPixelOptions(on=True))
    assert outgoing_msg == "on=1;"

    outgoing_msg = NeoPixelDuplexMessenger().compose_msg(NeoPixelOptions(on=False))
    assert outgoing_msg == "on=0;"


def test_compose_msg_twinkle():
    outgoing_msg = NeoPixelDuplexMessenger().compose_msg(NeoPixelOptions(twinkle=True))
    assert outgoing_msg == "twinkle=1;"

    outgoing_msg = NeoPixelDuplexMessenger().compose_msg(NeoPixelOptions(twinkle=False))
    assert outgoing_msg == "twinkle=0;"


def test_compose_msg_transform():
    outgoing_msg = NeoPixelDuplexMessenger().compose_msg(NeoPixelOptions(transform=True))
    assert outgoing_msg == "transform=1;"

    outgoing_msg = NeoPixelDuplexMessenger().compose_msg(NeoPixelOptions(transform=False))
    assert outgoing_msg == "transform=0;"


def test_compose_msg_ms():
    outgoing_msg = NeoPixelDuplexMessenger().compose_msg(NeoPixelOptions(ms=7))
    assert outgoing_msg == "ms=7;"

    outgoing_msg = NeoPixelDuplexMessenger().compose_msg(NeoPixelOptions(ms=209))
    assert outgoing_msg == "ms=209;"


def test_compose_msg_brightness():
    outgoing_msg = NeoPixelDuplexMessenger().compose_msg(NeoPixelOptions(brightness=24))
    assert outgoing_msg == "brightness=24;"

    outgoing_msg = NeoPixelDuplexMessenger().compose_msg(NeoPixelOptions(brightness=195))
    assert outgoing_msg == "brightness=195;"


def test_compose_msg_palette():
    outgoing_palette = [0,0,0,1,1,1,2,2,2,3,3,3,4,4,4,5,5,5,6,6,6,7,7,7,8,8,8]
    outgoing_msg = NeoPixelDuplexMessenger().compose_msg(NeoPixelOptions(palette=outgoing_palette))
    assert outgoing_msg == "palette=0,0,0,1,1,1,2,2,2,3,3,3,4,4,4,5,5,5,6,6,6,7,7,7,8,8,8;"

    outgoing_palette = [123,234,56,78,90,1,2,3,4,5,6,7,8,9,0,12,34,56,78,9,100,200,50,150,250,0,255]
    outgoing_msg = NeoPixelDuplexMessenger().compose_msg(NeoPixelOptions(palette=outgoing_palette))
    assert outgoing_msg == "palette=123,234,56,78,90,1,2,3,4,5,6,7,8,9,0,12,34,56,78,9,100,200,50,150,250,0,255;"


def test_compose_msg_pir_armed():
    outgoing_msg = NeoPixelDuplexMessenger().compose_msg(NeoPixelOptions(pir_armed=True))
    assert outgoing_msg == "pir_armed=1;"

    outgoing_msg = NeoPixelDuplexMessenger().compose_msg(NeoPixelOptions(pir_armed=False))
    assert outgoing_msg == "pir_armed=0;"


def test_compose_msg_pir_timeout():
    outgoing_msg = NeoPixelDuplexMessenger().compose_msg(NeoPixelOptions(pir_timeout_seconds=123))
    assert outgoing_msg == "pir_timeout=123;"

    outgoing_msg = NeoPixelDuplexMessenger().compose_msg(NeoPixelOptions(pir_timeout_seconds=234))
    assert outgoing_msg == "pir_timeout=234;"
