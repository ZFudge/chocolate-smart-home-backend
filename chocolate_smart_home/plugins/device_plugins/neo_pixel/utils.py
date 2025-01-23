from collections import namedtuple
from math import ceil
from typing import List

from chocolate_smart_home.schemas.utils import to_schema
from .model import NeoPixel
from .schemas import NeoPixelDevice, PIR


PaletteHexTuple = namedtuple(
    "PaletteHexTuple",
    ["hex1", "hex2", "hex3", "hex4", "hex5", "hex6", "hex7", "hex8", "hex9"],
)


def to_neo_pixel_schema(neo_pixel: NeoPixel) -> NeoPixelDevice:
    pir = None
    if neo_pixel.pir_armed is not None:
        pir = PIR(
            armed=neo_pixel.pir_armed,
            timeout_seconds=neo_pixel.pir_timeout_seconds
        )

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


def byte_list_to_hex_tuple(palette: List[str]) -> PaletteHexTuple:
    """Convert a flat list of RGB values to a list of hex strings."""
    # Break palette into chunks of 3 RGB values each
    mod_palette = [palette[x * 3 : x * 3 + 3] for x in range(ceil(len(palette) / 3))]
    # Convert each list chunk to a single hex string
    mod_palette = ["#" + "".join(map(lambda n: f"{n:02x}", x)) for x in mod_palette]
    return PaletteHexTuple(*mod_palette)
