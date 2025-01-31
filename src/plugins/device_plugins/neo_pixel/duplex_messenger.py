from types import MappingProxyType
from typing import Callable

from pydantic import ValidationError

from src.plugins.base_duplex_messenger import BaseDuplexMessenger
import src.plugins.device_plugins.neo_pixel.schemas as np_schemas
import src.plugins.device_plugins.neo_pixel.utils as utils


class NeoPixelDuplexMessenger(BaseDuplexMessenger):
    """Adapts data between app and MQTT."""

    OUTGOING_LOOKUP = MappingProxyType(
        {
            False: "0",
            True: "1",
        }
    )

    def parse_msg(self, incoming_msg: str) -> np_schemas.NeoPixelDeviceReceived:
        """Parse incoming MQTT message from controller."""
        device, msg_seq = super().parse_msg(incoming_msg)

        bools_byte = int(next(msg_seq))

        on = bools_byte & 1
        twinkle = bools_byte >> 1 & 1
        transform = bools_byte >> 2 & 1
        pir_enabled = bools_byte >> 4 & 1
        pir_armed = bools_byte >> 5 & 1

        ms = int(next(msg_seq))
        brightness = int(next(msg_seq))
        pir_timeout_seconds = int(next(msg_seq))

        palette = utils.received_controller_palette_value_to_hex_str_tuple(msg_seq)

        try:
            pir = None
            if pir_enabled:
                pir = np_schemas.PIR(
                    armed=pir_armed, timeout_seconds=pir_timeout_seconds
                )

            neo_pixel_device = np_schemas.NeoPixelDeviceReceived(
                on=on,
                twinkle=twinkle,
                transform=transform,
                ms=ms,
                brightness=brightness,
                palette=palette,
                device=device,
                pir=pir,
            )
        except ValidationError:
            raise

        return neo_pixel_device

    def serialize(self, data: np_schemas.NeoPixelDeviceReceived) -> dict:
        """Serialize neo pixel data for broadcast through webocket."""
        np_dict = data.model_dump()

        # TODO: check online status
        np_dict["online"] = True

        device_dict = super().serialize(data.device)
        del np_dict["device"]

        np_dict.update(device_dict)

        return np_dict

    def compose_msg(self, data: dict | np_schemas.NeoPixelOptions) -> str:
        """Compose outgoing message to be published through MQTT."""
        msg = ""

        if isinstance(data, np_schemas.NeoPixelOptions):
            data = data.model_dump()

        _add_bool_key_value = self._get_add_key_value_func(
            data, value_mutator=lambda x: NeoPixelDuplexMessenger.OUTGOING_LOOKUP[x]
        )
        _add_key_value = self._get_add_key_value_func(data)

        msg += _add_bool_key_value("on")
        msg += _add_bool_key_value("twinkle")
        msg += _add_bool_key_value("transform")

        msg += _add_key_value("ms")
        msg += _add_key_value("brightness")

        msg += _add_bool_key_value("pir_armed")
        msg += _add_key_value("pir_timeout_seconds", preferred_key="pir_timeout")

        if data.get("palette") is not None:
            # Palette is a list of 9 hex strings. Convert to a commas-separated list of 27 bytes
            # and embed in outgoing controller message
            palette_27_byte_str = utils.convert_9_hex_to_27_byte_str(data["palette"])
            msg += "palette={};".format(palette_27_byte_str)

        return msg

    @staticmethod
    def _get_add_key_value_func(
        data: dict, *, value_mutator=lambda x: x
    ) -> Callable[[dict, str], str]:
        """Return a function that adds a key value to a message string with an optional value mutator function."""

        def _func(key: str, *, preferred_key: str = None) -> str:
            if data.get(key) is None:
                return ""
            if preferred_key is None:
                preferred_key = key
            # Apply value mutator function to value, if it exists
            value = value_mutator(data[key])
            return f"{preferred_key}={value};"

        return _func


# Alias messenger for use in ..discovered_plugins.DISCOVERED_PLUGINS["neo_pixel"] dict.
DuplexMessenger = NeoPixelDuplexMessenger
