from pydantic import BaseModel

from chocolate_smart_home.schemas.device_type import DeviceType
from chocolate_smart_home.schemas.tag import Tag


class DeviceId(BaseModel):
    id: int


class DeviceBase(BaseModel):
    mqtt_id: str | int
    remote_name: str
    name: str
    device_type: DeviceType
    tag: Tag | None
    online: bool
    reboots: int


class Device(DeviceId, DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    mqtt_id: int
    device_type_name: str


class DeviceReceived(BaseModel):
    mqtt_id: int
    device_type_name: str
    remote_name: str


__all__ = [
    "DeviceBase",
    "Device",
    "DeviceReceived",
    "DeviceUpdate",
]
