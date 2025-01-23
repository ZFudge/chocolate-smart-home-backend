from typing import Callable


RECEIVE_DEVICE_DATA = "/receive_device_state/"
REQUEST_DEVICE_DATA_ALL = "/broadcast_request_devices_state/"
REQUEST_DEVICE_DATA_TEMPLATE = "/request_device_state/{device_id}/"
SEND_DEVICE_DATA_TEMPLATE = "/{device_type}/{{device_id}}/"


def get_format_topic_by_device_id(device_type_name: str) -> Callable[[int], str]:
    DEVICE_TOPIC_TEMPLATE = SEND_DEVICE_DATA_TEMPLATE.format(
        device_type=device_type_name
    )

    def format_topic_by_device_id(device_id: int) -> str:
        return DEVICE_TOPIC_TEMPLATE.format(device_id=device_id)

    return format_topic_by_device_id
