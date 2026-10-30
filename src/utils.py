import datetime as dt
import logging

from src.dependencies import get_request_all_device_data_last_sent_as_dt
from src.models.device import Device

logger = logging.getLogger(__name__)


async def is_online(device: Device | dict) -> bool:
    if isinstance(device, Device):
        last_seen = device.last_seen
        last_update_sent = device.last_update_sent
    else:
        last_seen = device.get("last_seen")
        last_update_sent = device.get("last_update_sent")

    online = False
    request_all_device_data_last_sent = (
        await get_request_all_device_data_last_sent_as_dt()
    )

    if all([last_update_sent, last_seen]):
        if (
            request_all_device_data_last_sent is None
            or (
                isinstance(request_all_device_data_last_sent, dt.datetime)
                and request_all_device_data_last_sent < last_seen
            )
        ) and last_update_sent < last_seen:
            online = True
    elif (
        last_seen
        and isinstance(request_all_device_data_last_sent, dt.datetime)
        and request_all_device_data_last_sent < last_seen
    ):
        online = True
    return online


def snakecase_to_pascalcase(string: str) -> str:
    return "".join(map(str.title, string.split("_")))
