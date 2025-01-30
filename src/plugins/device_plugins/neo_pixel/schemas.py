from typing import List, Tuple

from pydantic import BaseModel, Field, field_validator

from src.schemas.device import Device, DeviceReceived


class NeoPixelId(BaseModel):
    id: int


class PaletteValidator:
    @field_validator("palette")
    @classmethod
    def palette_must_contain_tag(
        cls, v: Tuple[*([int] * 27)]
    ) -> Tuple[*([int] * 27)]:
        if len(v) != 27:
            raise ValueError(
                f"Neo Pixel palette must have a length of 27. length: {len(v)}"
            )
        out_of_range_values = tuple(filter(lambda x: x < 0 or 255 < x, v))
        if out_of_range_values:
            raise ValueError(
                "Neo Pixel palette can only contain values between 0 and 255. "
                f"Received values out of range: {out_of_range_values}"
            )
        return v


class PIR(BaseModel):
    armed: bool
    timeout_seconds: int


class NeoPixelValues(BaseModel, PaletteValidator):
    on: bool
    twinkle: bool
    transform: bool
    ms: int = Field(None, ge=0, le=255)
    brightness: int = Field(None, ge=0, le=255)
    palette: Tuple[*([int] * 27)]
    pir: PIR | None = None


class NeoPixelOptions(BaseModel, PaletteValidator):
    on: bool = None
    twinkle: bool = None
    transform: bool = None
    ms: int = Field(None, ge=0, le=255)
    brightness: int = Field(None, ge=0, le=255)
    palette: Tuple[*([int] * 27)] = None
    pir_armed: bool = None
    pir_timeout_seconds: int | None = None


class NeoPixelDevices(BaseModel):
    mqtt_ids: List[int]
    data: NeoPixelOptions


class NeoPixelDevice(NeoPixelId, NeoPixelValues):
    device: Device


class NeoPixelDeviceReceived(NeoPixelValues):
    device: DeviceReceived
