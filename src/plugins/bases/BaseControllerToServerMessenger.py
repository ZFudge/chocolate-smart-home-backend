import logging
from collections.abc import Iterable

from src.models import Device as models_Device
from src.schemas import (
    DeviceFrontend as DeviceFrontendSchema,
)
from src.schemas import (
    DeviceReceived as DeviceReceivedSchema,
)
from src.schemas import (
    device_mod_obj_to_frontend_schema as to_frontend_schema,
)

logger = logging.getLogger()


class BaseControllerToServerMessenger:
    def parse_controller_msg(
        self,
        raw_msg: str,
    ) -> tuple[DeviceReceivedSchema, Iterable[str]]:
        """Parse message from remote controller."""
        msg_seq: Iterable[str] = iter(raw_msg.split(","))
        mqtt_id: int = int(next(msg_seq))
        device_type_name: str = ""
        remote_name: str = ""
        try:
            device_type_name = next(msg_seq)
            remote_name = next(msg_seq)
        except StopIteration:
            logger.warning(
                f"Not enough comma-separated values in message.payload. payload='{raw_msg}'."
            )
        device = DeviceReceivedSchema(
            mqtt_id=mqtt_id,
            device_type_name=device_type_name,
            remote_name=remote_name,
            name=remote_name,
        )
        return device, msg_seq

    @staticmethod
    def get_device_frontend(db_device: models_Device) -> DeviceFrontendSchema:
        return to_frontend_schema(db_device)


class DefaultControllerToServerMessenger(BaseControllerToServerMessenger):
    def parse_controller_msg(self, raw_msg: str) -> DeviceReceivedSchema:
        """Parse message from remote controller, omitting empty list iterator."""
        device_received_schema, _ = super().parse_controller_msg(raw_msg)
        return device_received_schema
