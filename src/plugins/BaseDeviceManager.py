import logging
from typing import Type

from src import crud, models, schemas
from src.database import Base
from .ValidateFEtoBEData import ValidateFEtoBEData

logger = logging.getLogger()


class BaseDeviceManager(ValidateFEtoBEData):
    # Set in subclasses to identify server-side values in the plugin's main model.
    SERVER_SIDE_COLUMNS = []

    @classmethod
    def is_server_side_value(cls, name: str) -> bool:
        """Returns true if given name matches a server-side value in the plugin's main model.
        This provides the implementation for both default plugins and plugins that implement their own models.
        """
        return name in cls.SERVER_SIDE_COLUMNS

    def update_server_side_value(self, data: dict):
        self.validate_msg_data(data)
        if not self.is_server_side_value(data["name"]):
            raise ValueError(f'{data["name"]} is not a server-side value')

    def get_device_by_id(self, mqtt_id: int) -> models.Device | None:
        return crud.get_device_by_id(mqtt_id)

    def create_device(self, device: schemas.DeviceReceived) -> models.Device:
        return crud.create_device(device)

    def update_device(self, device: schemas.DeviceReceived) -> models.Device:
        return crud.update_device(device)

    def commit_db_object(self, db_obj: Type[Base]) -> Type[Base]:
        return crud.commit_db_object(db_obj)

    def get_plugin_db_obj_using_device_type_and_mqtt_id(
        self, *, device_type_name: str, mqtt_id: int, **kwargs
    ):
        return crud.get_plugin_db_obj_using_device_type_and_mqtt_id(
            device_type_name, mqtt_id
        )
