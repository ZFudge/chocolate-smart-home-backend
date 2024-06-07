from pydantic import BaseModel

from chocolate_smart_home.schemas.client import Client
from chocolate_smart_home.schemas.device_name import DeviceName
from chocolate_smart_home.schemas.device_type import DeviceType
from chocolate_smart_home.schemas.space import Space, SpaceEmpty


class DeviceId(BaseModel):
    id: int


class DeviceBase(BaseModel):
    client: Client
    device_name: DeviceName
    device_type: DeviceType
    space: Space | SpaceEmpty
    remote_name: str
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
