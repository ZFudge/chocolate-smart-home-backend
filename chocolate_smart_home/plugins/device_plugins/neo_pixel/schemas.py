from typing import List, Tuple

from pydantic import BaseModel, Field, field_validator

from chocolate_smart_home.schemas.device import Device


class NeoPixelId(BaseModel):
    id: int


class PaletteValidator:
    @field_validator('palette')
    @classmethod
    def palette_must_contain_space(cls, v: Tuple[*([int]*27)]) -> Tuple[*([int]*27)]:
        if len(v) != 27:
            raise ValueError(f"Neo Pixel palette must have a length of 27. length: {len(v)}")
        out_of_range_values = tuple(filter(lambda x: x < 0 or 255 < x, v))
        if out_of_range_values:
            raise ValueError("Neo Pixel palette can only contain values between 0 and 255. "
                            f"Received values out of range: {out_of_range_values}")
        return v


class NeoPixelValues(BaseModel, PaletteValidator):
    on: bool
    twinkle: bool
    transform: bool
    ms: int = Field(None, ge=0, le=255)
    brightness: int = Field(None, ge=0, le=255)
    palette: Tuple[*([int]*27)]


class NeoPixelOptions(BaseModel, PaletteValidator):
    on: bool = None
    twinkle: bool = None
    transform: bool = None
    ms: int = Field(None, ge=0, le=255)
    brightness: int = Field(None, ge=0, le=255)
    palette: Tuple[*([int]*27)] = None


class NeoPixelDevices(BaseModel):
    ids: List[int]
    data: NeoPixelOptions


class NeoPixelDevice(NeoPixelId, NeoPixelValues):
    device: Device
