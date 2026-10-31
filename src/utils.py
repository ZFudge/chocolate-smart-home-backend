import datetime as dt
import logging

from src.dependencies import redis_session
from src.models.device import Device

logger = logging.getLogger(__name__)

REQUEST_ALL_DEVICE_DATA_LAST_SENT_KEY = "request_all_device_data_last_sent"


async def get_request_all_device_data_last_sent_as_dt() -> dt.datetime | None:
    last_sent = await redis_session.get().get(REQUEST_ALL_DEVICE_DATA_LAST_SENT_KEY)
    if not isinstance(last_sent, (int, str)):
        return
    try:
        return dt.datetime.fromtimestamp(int(last_sent))
    except (TypeError, ValueError) as e:
        logger.error(f"Error converting {last_sent=} to datetime: {e}")
        return


async def set_request_all_device_data_last_sent(last_sent_dt) -> None:
    if not isinstance(last_sent_dt, dt.datetime):
        raise TypeError("last_sent_dt must be a datetime object")
    timestamp = int(last_sent_dt.timestamp())
    await redis_session.get().set(REQUEST_ALL_DEVICE_DATA_LAST_SENT_KEY, timestamp)


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
    elif last_seen and (
        (
            isinstance(request_all_device_data_last_sent, dt.datetime)
            and request_all_device_data_last_sent < last_seen
        )
        or request_all_device_data_last_sent is None
    ):
        online = True

    return online


def snakecase_to_pascalcase(string: str) -> str:
    return "".join(map(str.title, string.split("_")))
