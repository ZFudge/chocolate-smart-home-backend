import pytest

from ..ServerToControllerMessenger import ServerToControllerMessenger


@pytest.fixture()
def ServerToControllerMessengerWithSuper():
    class BaseServerToControllerMessenger:
        def compose_controller_msg(self, msg_data: dict) -> str | None:
            return ""

        @staticmethod
        def _compose_param(key: str, val: str) -> str:
            return f"{key}={val};"

    class PluginServerToControllerMessenger(
        ServerToControllerMessenger, BaseServerToControllerMessenger
    ):
        pass

    yield PluginServerToControllerMessenger
