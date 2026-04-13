import logging

from src.crud import (
    create_device,
    get_device_by_id,
    update_device,
)
from src.models import Device as models_Device
from src.schemas import DeviceReceived as DeviceReceivedSchema


logger = logging.getLogger()


class BaseDeviceManager:
    def get_device_by_id(self, mqtt_id: int) -> models_Device | None:
        return get_device_by_id(mqtt_id)

    def create_device(self, device: DeviceReceivedSchema) -> models_Device:
        db_device = create_device(device)
        return db_device

    def update_device(self, device: DeviceReceivedSchema, *_) -> models_Device:
        db_device = update_device(device)
        return db_device
