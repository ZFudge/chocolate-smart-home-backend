import logging

from pydantic import BaseModel

from .Schema import OnOff

logger = logging.getLogger()


class ControllerToServerMessenger:
    def parse_controller_msg(
        self,
        raw_msg: str,
    ) -> type[BaseModel]:
        device_schema, msg_seq = super().parse_controller_msg(raw_msg)
        try:
            on_str: str = next(msg_seq)
            try:
                on = bool(int(on_str))
            except ValueError:
                raise ValueError(
                    f'Could not cast on_off plugin "on" value "{on_str}" from str->int->bool'
                ) from None
            device_schema.plugin = OnOff(on=on)
            return device_schema
        except StopIteration:
            raise StopIteration(
                f"Not enough comma-separated values in message payload '{raw_msg}'. on_off plugin could not parse message."
            ) from None
