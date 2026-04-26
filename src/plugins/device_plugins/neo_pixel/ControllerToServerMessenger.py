import logging

from pydantic import BaseModel, ValidationError

from . import Schema, utils

logger = logging.getLogger()


class ControllerToServerMessenger:
    def parse_controller_msg(
        self,
        raw_msg: str,
    ) -> type[BaseModel]:
        device_schema, msg_seq = super().parse_controller_msg(raw_msg)
        try:
            bools_byte = int(next(msg_seq))
            on = bool(bools_byte & 1)
            twinkle = bool(bools_byte >> 1 & 1)
            transform = bool(bools_byte >> 2 & 1)
            if twinkle:
                all_twinkle_colors_are_current = bool(bools_byte >> 3 & 1)
            else:
                all_twinkle_colors_are_current = None
            pir_enabled = bool(bools_byte >> 4 & 1)
            pir_armed = bool(bools_byte >> 5 & 1)

            ms = int(next(msg_seq))
            brightness = int(next(msg_seq))
            timeout = int(next(msg_seq))

            palette = utils.received_controller_palette_value_to_hex_str_tuple(msg_seq)

            try:
                device_schema.plugin = Schema.NeoPixel(
                    on=on,
                    twinkle=twinkle,
                    transform=transform,
                    ms=ms,
                    brightness=brightness,
                    palette=palette,
                    all_twinkle_colors_are_current=all_twinkle_colors_are_current,
                    pir_enabled=pir_enabled,
                    pir_armed=pir_armed,
                    pir_timeout=timeout,
                )
            except ValidationError:
                pass
            return device_schema
        except StopIteration:
            raise StopIteration(
                f"Not enough comma-separated values in message payload '{raw_msg}'. on_off plugin could not parse message."
            ) from None
