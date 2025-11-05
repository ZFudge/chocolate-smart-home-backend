from unittest.mock import patch
import pytest

from src.routers.websocket import handle_incoming_websocket_message


@pytest.mark.asyncio
async def test_leonardo_ws_to_duplex_messenger__compose_msg():
    incoming_data_dict = {
        "device_type_name": "leonardo",
        "id": 1,
        "name": "msg",
        "value": "wake",
    }
    with (
        patch("src.mqtt.client.MQTTClient.publish") as _,
        patch(
            "src.plugins.device_plugins.leonardo.duplex_messenger.LeonardoDuplexMessenger.compose_msg"
        ) as compose_msg,
    ):
        await handle_incoming_websocket_message(incoming_data_dict)
        compose_msg.assert_called_once_with(
            {
                "msg": "wake",
            }
        )


@pytest.mark.asyncio
async def test_leonardo_ws_to_duplex_messenger__compose_msg__invalid_message():
    incoming_data_dict = {
        "device_type_name": "leonardo",
        "id": 1,
        "name": "msg",
        "value": "invalid",
    }
    with patch("src.mqtt.client.MQTTClient.publish") as publish:
        with pytest.raises(ValueError):
            await handle_incoming_websocket_message(incoming_data_dict)
        publish.assert_not_called()


@pytest.mark.asyncio
async def test_leonardo_ws_msg_publish_through_mqtt():
    incoming_data_dict = {
        "device_type_name": "leonardo",
        "id": 1,
        "name": "msg",
        "value": "wake",
    }
    with patch("src.mqtt.client.MQTTClient.publish") as publish:
        await handle_incoming_websocket_message(incoming_data_dict)
        publish.assert_called_once_with(topic="/leonardo/1/", message="wake")
    incoming_data_dict["value"] = "lock"
    with patch("src.mqtt.client.MQTTClient.publish") as publish:
        await handle_incoming_websocket_message(incoming_data_dict)
        publish.assert_called_once_with(topic="/leonardo/1/", message="lock")
    incoming_data_dict["value"] = "unlock"
    with patch("src.mqtt.client.MQTTClient.publish") as publish:
        await handle_incoming_websocket_message(incoming_data_dict)
        publish.assert_called_once_with(topic="/leonardo/1/", message="unlock")
    incoming_data_dict["value"] = "talon"
    with patch("src.mqtt.client.MQTTClient.publish") as publish:
        await handle_incoming_websocket_message(incoming_data_dict)
        publish.assert_called_once_with(topic="/leonardo/1/", message="talon")


@pytest.mark.asyncio
async def test_leonardo_ws_msg_publish_through_mqtt__invalid_message():
    incoming_data_dict = {
        "device_type_name": "leonardo",
        "id": 1,
        "name": "msg",
        "value": "missing_message",
    }
    with patch("src.mqtt.client.MQTTClient.publish") as publish:
        with pytest.raises(ValueError):
            await handle_incoming_websocket_message(incoming_data_dict)
        publish.assert_not_called()
