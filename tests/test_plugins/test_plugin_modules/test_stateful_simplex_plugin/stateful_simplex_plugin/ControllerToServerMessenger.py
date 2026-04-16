import logging

from pydantic import BaseModel

from .Schema import StatefulSimplexPluginSchema

logger = logging.getLogger()


class ControllerToServerMessenger:
    def parse_controller_msg(
        self,
        raw_msg: str,
    ) -> type[BaseModel]:
        device_schema, msg_seq = super().parse_controller_msg(raw_msg)
        try:
            sensor_reading: str = next(msg_seq)
            try:
                sensor_reading = int(sensor_reading)
            except Exception:
                sensor_reading = -1
            device_schema.plugin = StatefulSimplexPluginSchema(
                sensor_reading=sensor_reading
            )
            return device_schema
        except StopIteration:
            raise StopIteration(
                f"Not enough comma-separated values in message.payload. payload='{raw_msg}'."
            ) from None
