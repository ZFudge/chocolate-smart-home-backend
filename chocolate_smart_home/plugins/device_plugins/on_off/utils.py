from chocolate_smart_home.schemas.utils import device_to_schema
from .model import OnOff
from .schemas import OnOffDeviceData


def on_off_device_to_full_device_data_schema(on_off: OnOff) -> OnOffDeviceData:
    return OnOffDeviceData(
        id=on_off.id,
        on=on_off.on,
        device=device_to_schema(on_off.device),
    )
