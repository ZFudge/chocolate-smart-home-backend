from ..ServerToControllerMessenger import ServerToControllerMessenger


def test_on_off_ServerToControllerMessenger_compose_controller_msg_invalid_name_returns_empty_string():
    assert (
        ServerToControllerMessenger().compose_controller_msg(
            {"name": "", "value": True}
        )
        == ""
    )
    assert ServerToControllerMessenger().compose_controller_msg({"on": True}) == ""


def test_on_off_ServerToControllerMessenger_compose_controller_msg_on():
    assert (
        ServerToControllerMessenger().compose_controller_msg(
            {"name": "on", "value": True}
        )
        == "1"
    )


def test_on_off_ServerToControllerMessenger_compose_controller_msg_off():
    assert (
        ServerToControllerMessenger().compose_controller_msg(
            {"name": "on", "value": False}
        )
        == "0"
    )
