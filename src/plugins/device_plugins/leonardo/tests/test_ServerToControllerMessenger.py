import pytest


def test_leonardo_ServerToControllerMessenger_compose_controller_msg_talon(
    ServerToControllerMessengerWithSuper,
):
    assert (
        ServerToControllerMessengerWithSuper().compose_controller_msg(
            {
                "mqtt_id": 123,
                "device_type_name": "",
                "name": "command",
                "value": "talon",
            }
        )
        == "talon"
    )


def test_leonardo_ServerToControllerMessenger_compose_controller_msg_unlock(
    ServerToControllerMessengerWithSuper,
):
    assert (
        ServerToControllerMessengerWithSuper().compose_controller_msg(
            {
                "mqtt_id": 123,
                "device_type_name": "",
                "name": "command",
                "value": "unlock",
            }
        )
        == "unlock"
    )


def test_leonardo_ServerToControllerMessenger_compose_controller_msg_lock(
    ServerToControllerMessengerWithSuper,
):
    assert (
        ServerToControllerMessengerWithSuper().compose_controller_msg(
            {
                "mqtt_id": 123,
                "device_type_name": "",
                "name": "command",
                "value": "lock",
            }
        )
        == "lock"
    )


def test_leonardo_ServerToControllerMessenger_compose_controller_msg_move(
    ServerToControllerMessengerWithSuper,
):
    assert (
        ServerToControllerMessengerWithSuper().compose_controller_msg(
            {
                "mqtt_id": 123,
                "device_type_name": "",
                "name": "command",
                "value": "move",
            }
        )
        == "move"
    )


def test_leonardo_ServerToControllerMessenger_compose_controller_msg_ValueError_when_empty(
    ServerToControllerMessengerWithSuper,
):
    with pytest.raises(KeyError):
        ServerToControllerMessengerWithSuper().compose_controller_msg({}) == ""


def test_leonardo_ServerToControllerMessenger_compose_controller_msg_ValueError_invalid_command(
    ServerToControllerMessengerWithSuper,
):
    with pytest.raises(ValueError, match='Invalid command: "invalid".'):
        ServerToControllerMessengerWithSuper().compose_controller_msg(
            {
                "mqtt_id": 123,
                "device_type_name": "",
                "name": "command",
                "value": "invalid",
            }
        )
