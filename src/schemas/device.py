from typing import List
from pydantic import BaseModel, field_validator

from src.schemas.device_type import DeviceType
from src.schemas.tag import Tag


class DeviceId(BaseModel):
    id: int


class DeviceBase(BaseModel):
    mqtt_id: str | int
    remote_name: str
    name: str
    device_type: DeviceType
    tags: List[Tag] | None
    online: bool
    reboots: int

    @field_validator("tags", mode="before")
    @classmethod
    def none_to_empty(cls, v: object) -> object:
        if v is None:
            return []
        return v


class Device(DeviceId, DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    mqtt_id: int
    device_type_name: str


class DeviceReceived(BaseModel):
    mqtt_id: int
    device_type_name: str
    remote_name: str
    name: str | None = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "name" not in kwargs:
            self.name = kwargs.get("remote_name")


__all__ = [
    "DeviceBase",
    "Device",
    "DeviceReceived",
    "DeviceUpdate",
]
