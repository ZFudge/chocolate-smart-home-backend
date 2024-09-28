from chocolate_smart_home.schemas.utils import to_schema
from .model import NeoPixel
from .schemas import NeoPixelDevice, PIR


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
