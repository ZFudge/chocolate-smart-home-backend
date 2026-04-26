import pytest

from ..ServerToControllerMessenger import ServerToControllerMessenger


def test_leonardo_ServerToControllerMessenger_compose_controller_msg_talon():
    assert (
        ServerToControllerMessenger().compose_controller_msg({"command": "talon"})
        == "talon"
    )


def test_leonardo_ServerToControllerMessenger_compose_controller_msg_unlock():
    assert (
        ServerToControllerMessenger().compose_controller_msg({"command": "unlock"})
        == "unlock"
    )


def test_leonardo_ServerToControllerMessenger_compose_controller_msg_lock():
    assert (
        ServerToControllerMessenger().compose_controller_msg({"command": "lock"})
        == "lock"
    )


def test_leonardo_ServerToControllerMessenger_compose_controller_msg_move():
    assert (
        ServerToControllerMessenger().compose_controller_msg({"command": "move"})
        == "move"
    )


def test_leonardo_ServerToControllerMessenger_compose_controller_msg_ValueError_when_empty():
    with pytest.raises(ValueError):
        ServerToControllerMessenger().compose_controller_msg({}) == ""


def test_leonardo_ServerToControllerMessenger_compose_controller_msg_ValueError_invalid_command():
    with pytest.raises(ValueError):
        ServerToControllerMessenger().compose_controller_msg({"command": "invalid"})


def test_leonardo_ServerToControllerMessenger_compose_controller_msg_TypeError():
    with pytest.raises(TypeError):
        ServerToControllerMessenger().compose_controller_msg("command")
