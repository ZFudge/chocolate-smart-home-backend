from typing import Optional

from pydantic import BaseModel


class DeviceId(BaseModel):
    id: int


class DeviceBase(BaseModel):
    mqtt_id: int
    remote_name: str
    name: str
    online: bool | None = False


class DeviceUpdate(BaseModel):
    id: int
    remote_name: Optional[str] | None = None
    name: Optional[str] | None = None
    online: Optional[bool] | None = None


class DeviceCreate(DeviceBase):
    pass


class Device(DeviceId, DeviceBase):
    pass


class Space(BaseModel):
    id: int
    name: str

    class ConfigDict:
        from_attributes = True
