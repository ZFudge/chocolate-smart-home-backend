from pydantic import BaseModel

from chocolate_smart_home.schemas.device_type import *
from chocolate_smart_home.schemas.space import *


class DeviceId(BaseModel):
    id: int


class DeviceBase(BaseModel):
    mqtt_id: int
    device_type: DeviceType
    remote_name: str
    name: str
    online: bool | None = False
    space: Space | None = None


class Device(DeviceId, DeviceBase):
    pass


class DeviceReceived(BaseModel):
    mqtt_id: int
    device_type_name: DeviceTypeBase
    remote_name: str
    
    def __init__(
        self,
        mqtt_id: int,
        device_type_name: str,
        remote_name: str,
        **kwargs
    ) -> None:
        super(DeviceReceived, self).__init__(
            mqtt_id=mqtt_id,
            device_type_name=DeviceTypeBase(name=device_type_name),
            remote_name=remote_name,
            **kwargs
        )


class DeviceCreate(DeviceReceived):
    device_type: DeviceType
    space: Space | None = None
    online: bool | None = False

__all__ = ["DeviceBase", "Device", "DeviceReceived", "DeviceCreate"]
