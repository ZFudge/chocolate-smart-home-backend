from unittest.mock import call, patch

import pytest

from src.routers.websocket import handle_incoming_websocket_message


@pytest.mark.asyncio
async def test_np_ws_msg__mqtt_publish():
    incoming_data_dict = {
        "device_type_name": "neo_pixel",
        "mqtt_id": 1,
        "name": "brightness",
        "value": 255,
    }

    with patch("src.mqtt.client.MQTTClient.publish") as publish:
        await handle_incoming_websocket_message(incoming_data_dict)
        publish.assert_called_once_with(
            topic="/neo_pixel/1/", message="brightness=255;"
        )


@pytest.mark.asyncio
async def test_np_ws_to__duplex_messenger__compose_msg():
    incoming_data_dict = {
        "device_type_name": "neo_pixel",
        "mqtt_id": 1,
        "name": "brightness",
        "value": 255,
    }

    with (
        patch("src.mqtt.client.MQTTClient.publish") as _,
        patch(
            "src.plugins.device_plugins.neo_pixel.duplex_messenger.NeoPixelDuplexMessenger.compose_msg"
        ) as compose_msg,
    ):
        await handle_incoming_websocket_message(incoming_data_dict)
        compose_msg.assert_called_once_with(
            {
                "brightness": 255,
            }
        )


@pytest.mark.asyncio
async def test_np_ws_msg__mqtt_publish__multiple_ids():
    incoming_data_dict = {
        "device_type_name": "neo_pixel",
        "mqtt_ids": [1, 2, 3],
        "name": "twinkle",
        "value": False,
    }

    with patch("src.mqtt.client.MQTTClient.publish") as publish:
        await handle_incoming_websocket_message(incoming_data_dict)
        expected_msg = "twinkle=0;"
        assert publish.call_args_list == [
            call(topic="/neo_pixel/1/", message=expected_msg),
            call(topic="/neo_pixel/2/", message=expected_msg),
            # MQTT ID 3 is not in the database, but should still be published
            call(topic="/neo_pixel/3/", message=expected_msg),
        ]


@pytest.mark.asyncio
async def test_np_ws_msg__duplex_messenger__compose_msg__multiple_ids():
    incoming_data_dict = {
        "device_type_name": "neo_pixel",
        "mqtt_ids": [1, 2, 3],
        "name": "twinkle",
        "value": True,
    }

    with (
        patch("src.mqtt.client.MQTTClient.publish") as _,
        patch(
            "src.plugins.device_plugins.neo_pixel.duplex_messenger.NeoPixelDuplexMessenger.compose_msg"
        ) as compose_msg,
    ):
        await handle_incoming_websocket_message(incoming_data_dict)
        compose_msg.assert_called_once_with(
            {
                "twinkle": True,
            }
        )
