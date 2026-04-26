from typing import Tuple

from pydantic import BaseModel, Field


class NeoPixel(BaseModel):
    on: bool = None
    twinkle: bool = None
    all_twinkle_colors_are_current: bool = None
    transform: bool = None
    ms: int = Field(None, ge=0, le=255)
    brightness: int = Field(None, ge=0, le=255)
    palette: Tuple[*([str] * 9)] = None
    scheduled_palette_rotation: bool = None
    # PIR values
    pir_enabled: bool = None
    pir_armed: bool = None
    pir_timeout: int | None = None
