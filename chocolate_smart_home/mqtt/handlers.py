from typing import Callable

from paho.mqtt.client import Client, MQTTMessage
from sqlalchemy.exc import NoResultFound

from chocolate_smart_home.models import Device, DeviceType


def get_device_data_received_handler(
    get_new_or_existing_device_type_by_name: Callable,
    get_device_by_mqtt_id: Callable,
    create_device: Callable,
    update_device: Callable,
    **kwargs
) -> Callable:
    def device_data_received(client: Client,
                             userdata: None,
                             message: MQTTMessage) -> Device:
        payload: str = message.payload.decode()
        print(payload)
        if payload is None:
            return
        payload_seq: list[str] = payload.split(",")
        (mqtt_id, device_type_name, remote_name) = payload_seq[:3]
        name: str = remote_name.split(" - ")[0]

        device_type: DeviceType = get_new_or_existing_device_type_by_name(device_type_name)

        try:
            _: Device = get_device_by_mqtt_id(mqtt_id)
        except NoResultFound:
            new_device: Device = create_device(
                mqtt_id,
                device_type_name=device_type.name,
                remote_name=remote_name,
                name=name
            )
            return new_device

        updated_device: Device = update_device(
            mqtt_id,
            device_type_name=device_type.name,
            remote_name=remote_name,
            name=name,
            online=True,
        )
        return updated_device

    return device_data_received
