from chocolate_smart_home.schemas.utils import to_schema
from .model import NeoPixel
from .schemas import NeoPixelDevice


def to_neo_pixel_schema(neo_pixel: NeoPixel) -> NeoPixelDevice:
    return NeoPixelDevice(
        id=neo_pixel.id,
        on=neo_pixel.on,
        device=to_schema(neo_pixel.device),
    )
