import logging
from typing import Iterable, Tuple

from src.models import Device as models_Device
from src.schemas import (
    device_mod_obj_to_frontend_schema as to_frontend_schema,
    DeviceFrontend as DeviceFrontendSchema,
    DeviceReceived as DeviceReceivedSchema,
)


logger = logging.getLogger()


class BaseControllerToServerMessenger:
    @staticmethod
    def parse_controller_msg(
        raw_msg: str,
    ) -> Tuple[DeviceReceivedSchema, Iterable[str]]:
        """Parse message from remote controller."""
        msg_seq: Iterable[str] = iter(raw_msg.split(","))
        try:
            mqtt_id: str = next(msg_seq)
            device_type_name: str = next(msg_seq)
            remote_name: str = next(msg_seq)
            device = DeviceReceivedSchema(
                mqtt_id=mqtt_id,
                device_type_name=device_type_name,
                remote_name=remote_name,
                name=remote_name,
            )
            return device, msg_seq
        except StopIteration:
            raise StopIteration(
                f"Not enough comma-separated values in message.payload. payload='{raw_msg}'."
            ) from None

    @staticmethod
    def get_device_frontend(db_device: models_Device) -> DeviceFrontendSchema:
        return to_frontend_schema(db_device)


class DefaultControllerToServerMessenger(BaseControllerToServerMessenger):
    def parse_controller_msg(self, raw_msg: str) -> DeviceReceivedSchema:
        """Parse message from remote controller, omitting empty list iterator."""
        device_received_schema, _ = super().parse_controller_msg(raw_msg)
        return device_received_schema
