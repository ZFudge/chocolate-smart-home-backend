from pydantic import BaseModel
from typing import List

from src.schemas.device_type import DeviceType


class DeviceId(BaseModel):
    mqtt_id: int


class DeviceBase(BaseModel):
    remote_name: str
    name: str
    reboots: int


class DeviceWithTagsAndDeviceType(BaseModel):
    tags: List[int] | None
    device_type: DeviceType


class Device(DeviceId, DeviceWithTagsAndDeviceType):
    pass


class DeviceUpdate(BaseModel):
    mqtt_id: int
    device_type_name: str


class UpdateDeviceName(BaseModel):
    name: str


class DeviceReceived(BaseModel):
    mqtt_id: int
    device_type_name: str
    remote_name: str
    name: str | None = None


class DeviceFrontend(DeviceId, DeviceBase):
    device_type_name: str
    tags: List[int] | None = None
    last_seen: str | None = None
    last_update_sent: str | None = None


class DevicePatch(BaseModel):
    mqtt_id: int
    tags: List[int] | None = None
    name: str | None = None


__all__ = [
    "Device",
    "DeviceBase",
    "DeviceFrontend",
    "DevicePatch",
    "DeviceReceived",
    "DeviceUpdate",
]
