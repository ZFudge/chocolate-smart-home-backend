from typing import List

from pydantic import BaseModel

from chocolate_smart_home.schemas.device import Device


class NeoPixelId(BaseModel):
    id: int


class NeoPixelValue(BaseModel):
    on: bool


class NeoPixelDevices(NeoPixelValue):
    ids: List[int]


class NeoPixelDevice(NeoPixelId, NeoPixelValue):
    device: Device
