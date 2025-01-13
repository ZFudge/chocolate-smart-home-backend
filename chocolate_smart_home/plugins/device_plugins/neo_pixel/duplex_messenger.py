from types import MappingProxyType

from pydantic import ValidationError

from chocolate_smart_home.plugins.base_duplex_messenger import BaseDuplexMessenger
import chocolate_smart_home.plugins.device_plugins.neo_pixel.schemas as np_schemas


class NeoPixelDuplexMessenger(BaseDuplexMessenger):
    """Adapts data between app and MQTT."""

    OUTGOING_LOOKUP = MappingProxyType({
        False: "0",
        True: "1",
    })

    def parse_msg(self, incoming_msg: str) -> np_schemas.NeoPixelDeviceReceived:
        """Parse incoming message from controller."""
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
        palette = tuple(map(int, [next(msg_seq) for _ in range(27)]))

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

    def compose_msg(self, data: np_schemas.NeoPixelOptions) -> str:
        """Compose outgoing message to be published to controller."""
        msg = ""

        if hasattr(data, "on") and data.on is not None:
            msg += "on={};".format(NeoPixelDuplexMessenger.OUTGOING_LOOKUP[data.on])

        if hasattr(data, "twinkle") and data.twinkle is not None:
            msg += "twinkle={};".format(
                NeoPixelDuplexMessenger.OUTGOING_LOOKUP[data.twinkle]
            )

        if hasattr(data, "transform") and data.transform is not None:
            msg += "transform={};".format(
                NeoPixelDuplexMessenger.OUTGOING_LOOKUP[data.transform]
            )

        if hasattr(data, "ms") and data.ms is not None:
            msg += "ms={};".format(data.ms)

        if hasattr(data, "brightness") and data.brightness is not None:
            msg += "brightness={};".format(data.brightness)

        if hasattr(data, "palette") and data.palette is not None:
            palette_str = ",".join(map(str, data.palette))
            msg += "palette={};".format(palette_str)

        if hasattr(data, "pir_armed") and data.pir_armed is not None:
            msg += "pir_armed={};".format(
                NeoPixelDuplexMessenger.OUTGOING_LOOKUP[data.pir_armed]
            )

        if (
            hasattr(data, "pir_timeout_seconds")
            and data.pir_timeout_seconds is not None
        ):
            msg += "pir_timeout={};".format(data.pir_timeout_seconds)

        return msg


# Alias messenger for use in ..discovered_plugins.DISCOVERED_PLUGINS["neo_pixel"] dict.
DuplexMessenger = NeoPixelDuplexMessenger
