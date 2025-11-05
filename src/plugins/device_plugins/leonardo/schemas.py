from typing import Literal

from pydantic import BaseModel

from src.schemas.device import Device, DeviceFrontend


class LeonardoId(BaseModel):
    id: int


class LeonardoMessage(BaseModel):
    msg: Literal["wake", "lock", "unlock", "talon"]


class LeonardoDevice(LeonardoId, LeonardoMessage):
    device: Device


class LeonardoDeviceFrontend(LeonardoMessage):
    device: DeviceFrontend
