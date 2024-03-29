from pydantic import BaseModel


class DeviceTypeId(BaseModel):
    id: int


class DeviceTypeBase(BaseModel):
    name: str


class DeviceType(DeviceTypeId, DeviceTypeBase):
    pass


class DeviceTypeCreate(DeviceTypeBase):
    pass


__all__ = ["DeviceTypeBase", "DeviceType", "DeviceTypeCreate"]
