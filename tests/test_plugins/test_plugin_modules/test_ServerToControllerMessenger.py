import pytest

from src.plugins.BaseServerToControllerMessenger import BaseServerToControllerMessenger


def test_BaseServerToControllerMessenger_compose_controller_msg_raises_ValueError():
    with pytest.raises(TypeError):
        BaseServerToControllerMessenger().compose_controller_msg("123")


def test_BaseServerToControllerMessenger_compose_controller_msg_returns_message():
    assert (
        BaseServerToControllerMessenger().compose_controller_msg(
            {
                "mqtt_id": 123,
                "name": "property",
                "value": 1,
                "device_type_name": "something",
            }
        )
        == "property=1;"
    )


def test_BaseServerToControllerMessenger__compose_param():
    assert BaseServerToControllerMessenger()._compose_param("k", 0) == "k=0;"
