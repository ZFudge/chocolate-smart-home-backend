import logging

from pydantic import BaseModel

from .Schema import StatefulDuplexPluginSchema

logger = logging.getLogger()


class ControllerToServerMessenger:
    def parse_controller_msg(
        self,
        raw_msg: str,
    ) -> type[BaseModel]:
        device_schema, msg_seq = super().parse_controller_msg(raw_msg)
        try:
            count: str = next(msg_seq)
            try:
                count = int(count)
            except Exception:
                count = -1
            device_schema.plugin = StatefulDuplexPluginSchema(count=count)
            return device_schema
        except StopIteration:
            raise StopIteration(
                f"Not enough comma-separated values in message.payload. payload='{raw_msg}'."
            ) from None
