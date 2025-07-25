from typing import List

from pydantic import BaseModel

from src.schemas.device import Device, DeviceFrontend, DeviceReceived


class OnOffId(BaseModel):
    id: int


class OnOffValue(BaseModel):
    on: bool


class OnOffDevices(OnOffValue):
    mqtt_ids: List[int]


class OnOffDevice(OnOffId, OnOffValue):
    device: Device


class OnOffDeviceReceived(OnOffValue):
    device: DeviceReceived


class OnOffDeviceFrontend(OnOffValue):
    device: DeviceFrontend
