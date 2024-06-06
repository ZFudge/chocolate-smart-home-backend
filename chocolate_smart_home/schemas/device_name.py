from pydantic import BaseModel


class DeviceNameId(BaseModel):
    id: int


class DeviceNameBase(BaseModel):
    name: str


class DeviceName(DeviceNameId, DeviceNameBase):
    is_server_side_name: bool


class DeviceNameUpdate(DeviceNameId, DeviceNameBase):
    pass


__all__ = [
    "DeviceName",
    "DeviceNameUpdate",
]
