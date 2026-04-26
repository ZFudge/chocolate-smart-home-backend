import pytest

from ..Schema import OnOff


def test_on_off_ControllerToServerMessenger_parse_controller_msg_on(
    ControllerToServerMessengerWithSuper,
):
    assert (
        ControllerToServerMessengerWithSuper()
        .parse_controller_msg("123,test_device_type_name,test_remote_name,1")
        .plugin.model_dump()
        == OnOff(
            on=True,
        ).model_dump()
    )


def test_on_off_ControllerToServerMessenger_parse_controller_msg_StopIteration(
    ControllerToServerMessengerWithSuper,
):
    with pytest.raises(StopIteration):
        ControllerToServerMessengerWithSuper().parse_controller_msg(
            "123,test_device_type_name,test_remote_name"
        )


def test_on_off_ControllerToServerMessenger_parse_controller_msg_ValueError(
    ControllerToServerMessengerWithSuper,
):
    with pytest.raises(ValueError):
        ControllerToServerMessengerWithSuper().parse_controller_msg(
            "123,test_device_type_name,test_remote_name,invalid"
        )
