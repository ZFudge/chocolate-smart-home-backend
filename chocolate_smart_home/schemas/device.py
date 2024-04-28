from pydantic import BaseModel

from chocolate_smart_home.schemas.device_type import DeviceType


class DeviceId(BaseModel):
    id: int


class DeviceBase(BaseModel):
    mqtt_id: int
    device_type: DeviceType
    remote_name: str
    name: str
    online: bool | None = False


class Device(DeviceId, DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    mqtt_id: int
    device_type_name: str


class DeviceReceived(BaseModel):
    mqtt_id: int
    device_type_name: str
    remote_name: str
    name: str | None = ""


__all__ = [
    "DeviceBase",
    "Device",
    "DeviceReceived",
    "DeviceUpdate",
]
