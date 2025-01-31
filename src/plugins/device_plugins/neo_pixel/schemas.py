from typing import List, Tuple

from pydantic import BaseModel, Field, field_validator

from src.schemas.device import Device, DeviceReceived


class NeoPixelId(BaseModel):
    id: int


class PaletteValidator:
    @field_validator("palette")
    @classmethod
    def palette_must_contain_tag(cls, v: Tuple[*([str] * 9)]) -> Tuple[*([str] * 9)]:
        if len(v) != 9:
            raise ValueError(
                f"Neo Pixel palette must have a length of 9. length: {len(v)}"
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
    palette: Tuple[*([str] * 9)]
    pir: PIR | None = None


class NeoPixelOptions(BaseModel, PaletteValidator):
    on: bool = None
    twinkle: bool = None
    transform: bool = None
    ms: int = Field(None, ge=0, le=255)
    brightness: int = Field(None, ge=0, le=255)
    palette: Tuple[*([str] * 9)] = None
    pir_armed: bool = None
    pir_timeout_seconds: int | None = None


class NeoPixelDevices(BaseModel):
    mqtt_ids: List[int]
    data: NeoPixelOptions


class NeoPixelDevice(NeoPixelId, NeoPixelValues):
    device: Device


class NeoPixelDeviceReceived(NeoPixelValues):
    device: DeviceReceived
