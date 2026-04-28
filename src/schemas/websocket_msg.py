from typing import List

from pydantic import BaseModel


class WebsocketMessage(BaseModel):
    device_type_name: str
    mqtt_id: List[int] | int | None = None
    name: str
    value: float | int | bool | List[str] | str


__all__ = ["WebsocketMessage"]
