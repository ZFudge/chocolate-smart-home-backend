from typing import List, Tuple

from pydantic import BaseModel, Field, field_validator

from src.schemas.device import Device, DeviceFrontend, DeviceReceived


def validate_hex_colors(v: Tuple[*([str] * 9)]) -> Tuple[*([str] * 9)]:
    if len(v) != 9:
        raise ValueError(
            f"Hex palette must have a length of 9. length: {len(v)}"
        )
    if not all(len(color) == 7 for color in v):
        raise ValueError("Each hex color should have a length of exactly 7")
    if not all(color.startswith("#") for color in v):
        raise ValueError("Each hex color should start with a #")
    if not all([all(['0' <= c <= 'f' for c in color[1:]]) for color in v]):
        raise ValueError("Each hex color should have valid hex digits")
    return v


def validate_bytes_colors(v: Tuple[*([int] * 27)]) -> Tuple[*([int] * 27)]:
    if len(v) != 27:
        raise ValueError(
            f"Bytes palette must have a length of 27. length: {len(v)}"
        )
    if not all(0 <= color <= 255 for color in v):
        raise ValueError("Each byte color should be between 0 and 255")
    return v


class NeoPixelId(BaseModel):
    id: int


class ValidateHexColors:
    @field_validator("palette")
    @classmethod
    def validate_hex_colors(cls, v: Tuple[*([str] * 9)]) -> Tuple[*([str] * 9)]:
        return validate_hex_colors(v)


class HexPaletteSchema(BaseModel, ValidateHexColors):
    id: int
    name: str
    palette: Tuple[str, ...]
    @field_validator("palette")
    @classmethod
    def validate_hex_colors(cls, v: Tuple[str, ...]) -> Tuple[str, ...]:
        return validate_hex_colors(v)


class ValidateBytesColors:
    @field_validator("palette")
    @classmethod
    def validate_bytes_colors(cls, v: Tuple[*([int] * 27)]) -> Tuple[*([int] * 27)]:
        return validate_bytes_colors(v)


class CreateBytesPaletteSchema(BaseModel, ValidateBytesColors):
    name: str
    palette: Tuple[int, ...]


class CreateHexPaletteSchema(BaseModel, ValidateHexColors):
    name: str
    palette: Tuple[str, ...]


class PIR(BaseModel):
    armed: bool
    timeout: int


class NeoPixelPaletteValidator:
    @field_validator("palette")
    @classmethod
    def palette_must_contain_tag(cls, v: Tuple[*([str] * 9)]) -> Tuple[*([str] * 9)]:
        return validate_hex_colors(v)


class NeoPixelValues(BaseModel, NeoPixelPaletteValidator):
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


class NeoPixelOptions(BaseModel, NeoPixelPaletteValidator):
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
