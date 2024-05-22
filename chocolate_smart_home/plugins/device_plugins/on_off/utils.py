from chocolate_smart_home.schemas.utils import device_type_to_schema
from .model import OnOff
from .schemas import OnOffDeviceData


def on_off_device_to_full_device_data_schema(on_off_device: OnOff) -> OnOffDeviceData:
    return OnOffDeviceData(
        id=on_off_device.id,
        on=on_off_device.on,
        mqtt_id=on_off_device.device.mqtt_id,
        device_type=device_type_to_schema(on_off_device.device.device_type),
        name=on_off_device.device.name,
        remote_name=on_off_device.device.remote_name,
        online=on_off_device.device.online,
    )
