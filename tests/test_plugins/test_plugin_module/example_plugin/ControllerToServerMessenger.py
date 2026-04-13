import logging
from typing import Any

from .schema import ExamplePluginSchema

logger = logging.getLogger()


class ControllerToServerMessenger:
    @staticmethod
    def parse_controller_msg(
        raw_msg: str,
    ) -> Any:
        """Parse message from remote controller."""
        primary_device_schema, msg_seq = super().parse_controller_msg(raw_msg)
        try:
            count: str = next(msg_seq)
            plugin_schema = ExamplePluginSchema(count=count)
            primary_device_schema.plugin = plugin_schema
            return primary_device_schema
        except StopIteration:
            raise StopIteration(
                f"Not enough comma-separated values in message.payload. payload='{raw_msg}'."
            ) from None
