from pydantic import BaseModel


class ClientId(BaseModel):
    id: int


class ClientMQTTId(BaseModel):
    mqtt_id: int


class Client(ClientId, ClientMQTTId):
    pass


class ClientUpdate(ClientId, ClientMQTTId):
    pass


__all__ = [
    "Client",
    "ClientUpdate",
]
