def test_on_off_ServerToControllerMessenger_compose_controller_msg_invalid_name_returns_empty_string(
    ServerToControllerMessengerWithSuper,
):
    assert (
        ServerToControllerMessengerWithSuper().compose_controller_msg(
            {"name": "", "value": True}
        )
        == ""
    )
    assert (
        ServerToControllerMessengerWithSuper().compose_controller_msg({"on": True})
        == ""
    )


def test_on_off_ServerToControllerMessenger_compose_controller_msg_on(
    ServerToControllerMessengerWithSuper,
):
    assert (
        ServerToControllerMessengerWithSuper().compose_controller_msg(
            {"name": "on", "value": True}
        )
        == "1"
    )


def test_on_off_ServerToControllerMessenger_compose_controller_msg_off(
    ServerToControllerMessengerWithSuper,
):
    assert (
        ServerToControllerMessengerWithSuper().compose_controller_msg(
            {"name": "on", "value": False}
        )
        == "0"
    )
