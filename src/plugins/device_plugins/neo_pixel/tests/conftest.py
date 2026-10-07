from unittest.mock import Mock

import pytest

from ..ControllerToServerMessenger import ControllerToServerMessenger
from ..DeviceManager import DeviceManager, Model
from ..ServerToControllerMessenger import ServerToControllerMessenger


@pytest.fixture()
def ControllerToServerMessengerWithSuper():
    class BaseControllerToServerMessenger:
        def parse_controller_msg(
            self,
            raw_msg: str,
        ):
            return Mock(), iter(raw_msg.split(",")[3:])

    class ControllerToServerMessengerWithSuper(
        ControllerToServerMessenger, BaseControllerToServerMessenger
    ):
        pass

    yield ControllerToServerMessengerWithSuper


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


@pytest.fixture()
def DeviceManagerWithSuper_and_mocked_PluginModel():
    Model.PluginModel = Mock()

    class BaseDeviceManager(Mock):
        pass

    BaseDeviceManager.create_device = Mock(return_value="create_db_device")
    BaseDeviceManager.update_device = Mock(return_value="updated_db_device")
    BaseDeviceManager.update_server_side_value = Mock(
        return_value="update_server_side_value"
    )
    BaseDeviceManager.commit_db_object = Mock()

    class DeviceManagerWithSuper(DeviceManager, BaseDeviceManager):
        pass

    yield DeviceManagerWithSuper, Model.PluginModel
