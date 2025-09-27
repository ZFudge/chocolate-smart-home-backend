from typing import List, Tuple

from pydantic import BaseModel, Field, field_validator

from src.schemas.device import Device, DeviceFrontend, DeviceReceived


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


class HexPaletteSchema(BaseModel):
    id: int
    name: str
    colors: Tuple[str, ...]


class PIR(BaseModel):
    armed: bool
    timeout: int


class NeoPixelValues(BaseModel, PaletteValidator):
    on: bool
    twinkle: bool
    transform: bool
    # This value is read-only from the controller. It is not updated by user.
    all_twinkle_colors_are_current: bool | None = None
    # This is only used server side and not sent to the controller.
    scheduled_palette_rotation: bool | None = None
    ms: int = Field(None, ge=0, le=255)
    brightness: int = Field(None, ge=0, le=255)
    palette: Tuple[*([str] * 9)]
    pir: PIR | None = None


class NeoPixelOptions(BaseModel, PaletteValidator):
    on: bool = None
    # START twinkle
    twinkle: bool = None
    # This value is read-only from the controller. It is not updated by user.
    all_twinkle_colors_are_current: bool = None
    # This is only used server side and not sent to the controller.
    # scheduled_palette_rotation: bool = None
    # END twinkle
    transform: bool = None
    ms: int = Field(None, ge=0, le=255)
    brightness: int = Field(None, ge=0, le=255)
    palette: Tuple[*([str] * 9)] = None
    armed: bool = None
    timeout: int | None = None


class NeoPixelDevices(BaseModel):
    mqtt_ids: List[int]
    data: NeoPixelOptions


class NeoPixelDevice(NeoPixelId, NeoPixelValues):
    device: Device


class NeoPixelDeviceReceived(NeoPixelValues):
    device: DeviceReceived

class NeoPixelDeviceFrontend(NeoPixelValues):
    device: DeviceFrontend
