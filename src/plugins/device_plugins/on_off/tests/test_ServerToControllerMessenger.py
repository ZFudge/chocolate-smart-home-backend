from ..ServerToControllerMessenger import ServerToControllerMessenger


def test_on_off_ServerToControllerMessenger_compose_controller_msg_empty():
    assert ServerToControllerMessenger().compose_controller_msg({}) == ""


def test_on_off_ServerToControllerMessenger_compose_controller_msg_on():
    assert ServerToControllerMessenger().compose_controller_msg({"on": True}) == "1"


def test_on_off_ServerToControllerMessenger_compose_controller_msg_off():
    assert ServerToControllerMessenger().compose_controller_msg({"on": False}) == "0"
