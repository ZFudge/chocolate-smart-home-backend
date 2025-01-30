from unittest.mock import patch

from chocolate_smart_home.routers.websocket import handle_incoming_websocket_message


def test_on_off_ws_to_duplex_messenger__compose_msg():
    incoming_data_dict = {
        "device_type_name": "on_off",
        "id": 1,
        "name": "on",
        "value": False,
    }
    with (
        patch("chocolate_smart_home.mqtt.client.MQTTClient.publish") as _,
        patch(
            "chocolate_smart_home.plugins.device_plugins.on_off.duplex_messenger.OnOffDuplexMessenger.compose_msg"
        ) as compose_msg,
    ):
        handle_incoming_websocket_message(incoming_data_dict)
        compose_msg.assert_called_once_with(
            {
                "on": False,
            }
        )


def test_on_off_ws_msg_publish_through_mqtt():
    incoming_data_dict = {
        "device_type_name": "on_off",
        "id": 1,
        "name": "on",
        "value": True,
    }
    with patch("chocolate_smart_home.mqtt.client.MQTTClient.publish") as publish:
        handle_incoming_websocket_message(incoming_data_dict)
        publish.assert_called_once_with(topic="/on_off/1/", message="1")
