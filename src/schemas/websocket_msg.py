from typing import List
from pydantic import BaseModel, model_validator


class WebsocketMessage(BaseModel):
    device_type_name: str
    name: str
    value: float | int | bool | List[str] | str

    # Some id fields are duplicated to support legacy ui.
    # TODO: remove legacy fields after migration
    ids: List[int] | int | None = None
    id: List[int] | int | None = None
    mqtt_ids: List[int] | int | None = None
    mqtt_id: List[int] | int | None = None

    def get_mqtt_ids(self) -> List[int]:
        ids = self.ids or self.mqtt_ids or self.id or self.mqtt_id
        if isinstance(ids, int):
            return [ids]
        return ids

    @model_validator(mode="before")
    @classmethod
    def validate_id_fields(cls, values):
        id_fields = ["ids", "id", "mqtt_ids", "mqtt_id"]
        present_fields = [field for field in id_fields if values.get(field) is not None]

        if len(present_fields) != 1:
            raise ValueError(
                "Exactly one of ids, id, mqtt_ids, or mqtt_id must be provided"
            )

        return values


__all__ = ["WebsocketMessage"]
