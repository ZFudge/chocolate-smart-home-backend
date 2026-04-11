from typing import Callable, List


# Incoming data from controllers
RECEIVE_DEVICE_DATA = "/receive_device_state/"
# Outgoing request for data, to controllers
REQUEST_DEVICE_DATA_ALL = "/broadcast_request_devices_state/"
# Outgoing request for data, to controller by mqtt id
REQUEST_DEVICE_DATA_TEMPLATE = "/request_device_state/{mqtt_id}/"
# Outgoing data to controllers
SEND_DEVICE_DATA_TEMPLATE = "/{device_type}/{{mqtt_id}}/"


def get_format_topic_by_mqtt_id_using_device_type_name(
    device_type_name: str,
) -> Callable[[int | List[int]], str | List[str]]:
    DEVICE_TOPIC_TEMPLATE = SEND_DEVICE_DATA_TEMPLATE.format(
        device_type=device_type_name
    )

    def format_topic_by_mqtt_id(mqtt_id: int | List[int]) -> str | List[str]:
        if isinstance(mqtt_id, list):
            return [
                DEVICE_TOPIC_TEMPLATE.format(mqtt_id=mqtt_id) for mqtt_id in mqtt_id
            ]
        return DEVICE_TOPIC_TEMPLATE.format(mqtt_id=mqtt_id)

    return format_topic_by_mqtt_id
