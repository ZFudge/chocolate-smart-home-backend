from chocolate_smart_home import models
from chocolate_smart_home.schemas.device import Device
from chocolate_smart_home.schemas.device_type import DeviceType


def device_type_to_schema(device_type_data: models.Device) -> DeviceType:
    return DeviceType(id=device_type_data.id, name=device_type_data.name)


def device_to_schema(device_data: models.Device) -> Device:
    return Device(
        id=device_data.id,
        mqtt_id=device_data.mqtt_id,
        device_type=device_type_to_schema(device_data.device_type),
        name=device_data.name,
        remote_name=device_data.remote_name,
        online=device_data.online,
    )
