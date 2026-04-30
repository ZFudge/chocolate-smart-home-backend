from pydantic import BaseModel
from typing import Any


class DeviceId(BaseModel):
    mqtt_id: int


class DeviceBase(BaseModel):
    remote_name: str
    name: str
    reboots: int


class DeviceReceived(BaseModel):
    mqtt_id: int
    device_type_name: str = ""
    remote_name: str = ""
    name: str = ""
    plugin: Any = None


class DeviceFrontend(DeviceId, DeviceBase):
    device_type_name: str
    tags: list[int] | None = None
    last_seen: str | None = None
    last_update_sent: str | None = None
    plugin: Any = None


class DevicePatch(BaseModel):
    mqtt_id: int
    tags: list[int] | None = None
    name: str | None = None


__all__ = [
    "DeviceBase",
    "DeviceFrontend",
    "DevicePatch",
    "DeviceReceived",
]
