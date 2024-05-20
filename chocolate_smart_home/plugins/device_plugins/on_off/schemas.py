from typing import List

from pydantic import BaseModel

from chocolate_smart_home.schemas.device import Device


# class OnOffDeviceId(BaseModel):
#     id: int

class OnOffValue(BaseModel):
    on: bool

class OnOffDevices(OnOffValue):
    ids: List[int]
    # on: bool
    # ids: List[OnOffDeviceId]

class OnOffDeviceData(Device, OnOffValue):
    pass
