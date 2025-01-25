from typing import List

from pydantic import BaseModel

from chocolate_smart_home.schemas.device import Device, DeviceReceived


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
