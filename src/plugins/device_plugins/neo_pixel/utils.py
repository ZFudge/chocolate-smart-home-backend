from collections import namedtuple
from logging import getLogger
from typing import Iterator, List


from src.schemas.utils import to_schema
from .model import NeoPixel
from .schemas import NeoPixelDevice, PIR

logger = getLogger(__name__)

PaletteHexNamedTuple = namedtuple(
    "PaletteHexNamedTuple",
    ["hex1", "hex2", "hex3", "hex4", "hex5", "hex6", "hex7", "hex8", "hex9"],
)


def to_neo_pixel_schema(neo_pixel: NeoPixel) -> NeoPixelDevice:
    pir = None
    if neo_pixel.armed is not None:
        pir = PIR(armed=neo_pixel.armed, timeout=neo_pixel.timeout)

    return NeoPixelDevice(
        id=neo_pixel.id,
        on=neo_pixel.on,
        twinkle=neo_pixel.twinkle,
        transform=neo_pixel.transform,
        ms=neo_pixel.ms,
        brightness=neo_pixel.brightness,
        palette=neo_pixel.palette,
        pir=pir,
        device=to_schema(neo_pixel.device),
    )


PaletteByteNamedTuple = namedtuple(
    "PaletteByteNamedTuple",
    list(map(lambda x: f"byte{x+1}", range(27))),
)


def hex_to_byte(x: str) -> int:
    """Convert a hex string to a byte."""
    return int(x, 16)


def hex_list_to_byte_tuple(palette: List[str]) -> PaletteByteNamedTuple:
    """Convert a list of 9 hex strings to a tuple of 27 bytes."""
    palette_bytes = []
    for hex_str in palette:
        hex_bytes = [hex_str[1 + i * 2 : 3 + i * 2] for i in range(3)]
        palette_bytes.extend(map(hex_to_byte, hex_bytes))
    return PaletteByteNamedTuple(*palette_bytes)


def convert_9_hex_to_27_byte_str(palette: List[str]) -> str:
    """Convert a list of 9 hex strings to a comma separated string of 27 bytes."""
    palette_bytes: PaletteByteNamedTuple = hex_list_to_byte_tuple(palette)
    return ",".join(map(str, palette_bytes))


def received_controller_palette_value_to_hex_str_tuple(
    msg_seq: Iterator[str],
) -> PaletteHexNamedTuple:
    """Convert iterator of 27 byte strings to named tuple of 9 hex strings."""
    try:
        complete_hex_strs = []
        current_hex = "#"
        for _ in range(27):
            byte_str = next(msg_seq)
            hex_str = f"{int(byte_str):x}".zfill(2)
            current_hex += hex_str
            if len(current_hex) == 7:
                complete_hex_strs.append(current_hex)
                current_hex = "#"
        return PaletteHexNamedTuple(*complete_hex_strs)
    except StopIteration as e:
        logger.error(e)
        logger.error(
            "Controller palette message must be 27 comma-separated byte strings long, "
            "but iteration interrupted early: type(msg_seq)=%s, complete_hex_strs=%s, current_hex=%s"
            % (type(msg_seq), complete_hex_strs, current_hex)
        )
        logger.info("Returning default empty palette")
        return PaletteHexNamedTuple(*[""] * 9)
    except ValueError as e:
        logger.error(e)
        logger.info("Returning default empty palette")
        return PaletteHexNamedTuple(*[""] * 9)
