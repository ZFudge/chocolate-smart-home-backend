import logging
from types import MappingProxyType
from typing import Callable, List

from pydantic import ValidationError

from src.plugins.base_duplex_messenger import BaseDuplexMessenger
from src.schemas.tag import Tag
import src.plugins.device_plugins.neo_pixel.schemas as np_schemas
import src.plugins.device_plugins.neo_pixel.utils as utils
from src.plugins.device_plugins.neo_pixel.schemas import NeoPixelDeviceFrontend
from .model import NeoPixel

logger = logging.getLogger()


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
        logger.info("Parsing incoming MQTT message from controller: %s" % incoming_msg)
        device, msg_seq = super().parse_msg(incoming_msg)

        bools_byte = int(next(msg_seq))

        on = bools_byte & 1
        twinkle = bools_byte >> 1 & 1
        transform = bools_byte >> 2 & 1
        all_twinkle_colors_are_current = bools_byte >> 3 & 1
        if not twinkle:
            all_twinkle_colors_are_current = None
        pir_enabled = bools_byte >> 4 & 1
        armed = bools_byte >> 5 & 1

        ms = int(next(msg_seq))
        brightness = int(next(msg_seq))
        timeout = int(next(msg_seq))

        palette = utils.received_controller_palette_value_to_hex_str_tuple(msg_seq)

        try:
            pir = None
            if pir_enabled:
                pir = np_schemas.PIR(armed=armed, timeout=timeout)

            neo_pixel_device = np_schemas.NeoPixelDeviceReceived(
                on=on,
                twinkle=twinkle,
                all_twinkle_colors_are_current=all_twinkle_colors_are_current,
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

        device_dict = super().serialize(data.device)
        del np_dict["device"]

        np_dict.update(device_dict)

        if np_dict.get("pir"):
            np_dict.update(np_dict["pir"])
            del np_dict["pir"]

        return np_dict

    def serialize_db_objects(self, data: NeoPixel | List[NeoPixel]) -> dict:
        """Serialize neo pixel data for broadcast through webocket."""
        if not isinstance(data, (list, tuple, set)):
            data = [data]
        serialized_data = []

        for db_neo_pixel in data:
            device = np_schemas.DeviceFrontend(
                mqtt_id=db_neo_pixel.device.mqtt_id,
                device_type_name="neo_pixel",
                remote_name=db_neo_pixel.device.name,
                last_seen=str(db_neo_pixel.device.last_seen),
            )
            if db_neo_pixel.device.tags:
                device.tags = [Tag(id=tag.id, name=tag.name) for tag in db_neo_pixel.device.tags]

            pir = None
            if db_neo_pixel.armed is not None:
                pir = np_schemas.PIR(
                    armed=db_neo_pixel.armed,
                    timeout=db_neo_pixel.timeout,
                )

            np_data = NeoPixelDeviceFrontend(
                device=device,
                on=db_neo_pixel.on,
                twinkle=db_neo_pixel.twinkle,
                all_twinkle_colors_are_current=db_neo_pixel.all_twinkle_colors_are_current,
                scheduled_palette_rotation=db_neo_pixel.scheduled_palette_rotation,
                transform=db_neo_pixel.transform,
                ms=db_neo_pixel.ms,
                brightness=db_neo_pixel.brightness,
                palette=db_neo_pixel.palette,
                pir=pir,
            )
            serialized_data.append(self.serialize(np_data))

        return serialized_data

    @staticmethod
    def _get_add_key_value_func(
        data: dict, *, value_mutator=lambda x: x
    ) -> Callable[[dict, str], str]:
        """Return a function that adds a key value to a message string with an optional value mutator function."""
        def _func(key: str, *, preferred_key: str | None = None) -> str:
            if data.get(key) is None:
                return ""
            if preferred_key is None:
                preferred_key = key
            # Apply value mutator function to value, if it exists
            value = value_mutator(data[key])
            return f"{preferred_key}={value};"
        return _func

    def compose_msg(self, data: dict | np_schemas.NeoPixelOptions) -> str | None:
        """Compose outgoing message to be published through MQTT."""
        if isinstance(data, np_schemas.NeoPixelOptions):
            data = data.model_dump()

        if data.get("scheduled_palette_rotation") is False:
            logger.info(
                "Skipping outgoing message because scheduled_palette_rotation is False"
            )
            return None

        msg = ""

        _add_bool_key_value = self._get_add_key_value_func(
            data, value_mutator=lambda x: NeoPixelDuplexMessenger.OUTGOING_LOOKUP[x]
        )
        _add_key_value = self._get_add_key_value_func(data)

        msg += _add_bool_key_value("on")
        msg += _add_bool_key_value("twinkle")
        msg += _add_bool_key_value("transform")

        msg += _add_key_value("ms")
        msg += _add_key_value("brightness")

        msg += _add_bool_key_value("armed")
        msg += _add_key_value("timeout") #, preferred_key="pir_timeout")

        if data.get("palette") is not None:
            # Palette is a list of 9 hex strings. Convert to a commas-separated list of 27 bytes
            # and embed in outgoing controller message
            palette_27_byte_str = utils.convert_9_hex_to_27_byte_str(data["palette"])
            msg += "palette={};".format(palette_27_byte_str)

        return msg


# Alias messenger for use in ..discovered_plugins.DISCOVERED_PLUGINS["neo_pixel"] dict.
DuplexMessenger = NeoPixelDuplexMessenger
