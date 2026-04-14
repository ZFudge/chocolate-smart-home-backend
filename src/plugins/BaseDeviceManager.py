import logging
from typing import Type

from src.crud import (
    commit_db_object,
    create_device,
    get_device_by_id,
    get_plugin_db_obj_using_device_type_and_mqtt_id,
    update_device,
)
from src.database import Base
from src.models import Device as models_Device
from src.schemas import DeviceReceived as DeviceReceivedSchema


logger = logging.getLogger()


class BaseDeviceManager:
    def get_device_by_id(self, mqtt_id: int) -> models_Device | None:
        return get_device_by_id(mqtt_id)

    def create_device(self, device: DeviceReceivedSchema) -> models_Device:
        return create_device(device)

    def update_device(self, device: DeviceReceivedSchema, *_) -> models_Device:
        return update_device(device)

    def commit_db_object(self, db_obj: Type[Base]) -> Type[Base]:
        return commit_db_object(db_obj)

    def get_plugin_db_obj_using_device_type_and_mqtt_id(
        self, *, device_type_name: str, mqtt_id: int, **kwargs
    ):
        get_plugin_db_obj_using_device_type_and_mqtt_id(device_type_name, mqtt_id)
