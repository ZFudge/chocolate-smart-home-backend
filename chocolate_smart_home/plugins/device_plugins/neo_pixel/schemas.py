from typing import List

from pydantic import BaseModel

from chocolate_smart_home.schemas.device import Device


class NeoPixelId(BaseModel):
    id: int


class NeoPixelValue(BaseModel):
    on: bool
    twinkle: bool
    transform: bool
    ms: int
    brightness: int


class NeoPixelOptions(BaseModel):
    on: bool = None
    twinkle: bool = None
    transform: bool = None
    ms: int = None
    brightness: int = None


class NeoPixelDevices(BaseModel):
    ids: List[int]
    data: NeoPixelOptions


class NeoPixelDevice(NeoPixelId, NeoPixelValue):
    device: Device
