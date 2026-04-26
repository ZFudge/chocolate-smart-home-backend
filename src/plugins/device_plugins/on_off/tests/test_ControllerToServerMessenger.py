from ..Schema import OnOff


def test_on_off_ControllerToServerMessenger_parse_controller_msg(
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
