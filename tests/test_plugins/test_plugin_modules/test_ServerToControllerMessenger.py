from src.plugins.BaseServerToControllerMessenger import BaseServerToControllerMessenger


def test_BaseServerToControllerMessenger_compose_controller_msg_returns_input():
    assert BaseServerToControllerMessenger().compose_controller_msg("123") == "123"


def test_BaseServerToControllerMessenger_compose_controller_msg_handles_arbitrary_args_and_kwargs():
    BaseServerToControllerMessenger().compose_controller_msg(
        "123", 0, True, a=1, b=2, c=3
    )


def test_BaseServerToControllerMessenger__compose_param():
    assert BaseServerToControllerMessenger()._compose_param("k", 0) == "&k=0"
