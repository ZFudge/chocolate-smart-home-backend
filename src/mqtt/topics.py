from typing import Callable, List


# Incoming data from controllers
RECEIVE_DEVICE_DATA = "/receive_device_state/"
# Outgoing request for data, to controllers
REQUEST_DEVICE_DATA_ALL = "/broadcast_request_devices_state/"
# Outgoing request for data, to controller by mqtt id
REQUEST_DEVICE_DATA_TEMPLATE = "/request_device_state/{mqtt_id}/"
# Outgoing data to controllers
SEND_DEVICE_DATA_TEMPLATE = "/{device_type}/{{mqtt_id}}/"


def get_format_topic_by_mqtt_id(device_type_name: str) -> Callable[[int], str]:
    DEVICE_TOPIC_TEMPLATE = SEND_DEVICE_DATA_TEMPLATE.format(
        device_type=device_type_name
    )

    def format_topic_by_mqtt_id(mqtt_id: int | List[int]) -> str:
        if isinstance(mqtt_id, list):
            return DEVICE_TOPIC_TEMPLATE.format(mqtt_id=mqtt_id[0])
        return DEVICE_TOPIC_TEMPLATE.format(mqtt_id=mqtt_id)

    return format_topic_by_mqtt_id
