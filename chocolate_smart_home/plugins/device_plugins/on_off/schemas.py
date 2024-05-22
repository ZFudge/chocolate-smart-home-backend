from typing import List

from pydantic import BaseModel

from chocolate_smart_home.schemas.device import Device


class OnOffValue(BaseModel):
    on: bool


class OnOffDevices(OnOffValue):
    ids: List[int]


class OnOffDeviceData(Device, OnOffValue):
    pass
