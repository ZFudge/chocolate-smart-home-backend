from typing import Callable

from paho.mqtt.client import Client, MQTTMessage
from sqlalchemy.exc import NoResultFound

from chocolate_smart_home.models import Device, DeviceType


class MQTTMessageHandler:
    def __init__(
        self,
        get_new_or_existing_device_type_by_name: Callable,
        get_device_by_mqtt_id: Callable,
        create_device: Callable,
        update_device: Callable,
        **kwargs
    ):
        self.get_new_or_existing_device_type_by_name = get_new_or_existing_device_type_by_name
        self.get_device_by_mqtt_id = get_device_by_mqtt_id
        self.create_device = create_device
        self.update_device = update_device

    def device_data_received(
        self,
        client: Client,
        userdata: None,
        message: MQTTMessage,
    ) -> Device:
        payload: str = message.payload.decode()
        print(payload)
        if payload is None:
            return
        payload_seq: list[str] = payload.split(",")
        (mqtt_id, device_type_name, remote_name) = payload_seq[:3]
        name: str = remote_name.split(" - ")[0]

        device_type: DeviceType = self.get_new_or_existing_device_type_by_name(device_type_name)

        try:
            _: Device = self.get_device_by_mqtt_id(mqtt_id)
        except NoResultFound:
            new_device: Device = self.create_device(
                mqtt_id,
                device_type_name=device_type.name,
                remote_name=remote_name,
                name=name
            )
            return new_device

        updated_device: Device = self.update_device(
            mqtt_id,
            device_type_name=device_type.name,
            remote_name=remote_name,
            name=name
        )
        return updated_device
