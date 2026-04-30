from pydantic import BaseModel


class WebsocketMessage(BaseModel):
    device_type_name: str
    mqtt_id: list[int] | int | None = None
    name: str
    value: float | int | bool | list[str] | str


__all__ = ["WebsocketMessage"]
