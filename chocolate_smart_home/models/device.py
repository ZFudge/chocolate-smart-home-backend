from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import relationship

from chocolate_smart_home.database import Base
from .client import Client
from .device_name import DeviceName
from .model_str_formatter import ModelStrFormatter


class DeviceClientError(SQLAlchemyError):
    def __init__(self, text="", client=None):
        if client is not None:
            text = (
                "Client object with mqtt_id of %s is already "
                "assigned to Device object of Device.id %s"
            ) % (client.mqtt_id, client.device.id)
        super().__init__(text)


class DeviceNameError(SQLAlchemyError):
    def __init__(self, text="", device_name=None):
        if device_name is not None:
            text = (
                "DeviceName object with DeviceName.name of %s is already "
                "assigned to Device object of Device.id %s"
            ) % (device_name.name, device_name.device.id)
        super().__init__(text)
    

class Device(Base, ModelStrFormatter):
    __tablename__ = "devices"
    __table_args__ = (UniqueConstraint("client_id"), UniqueConstraint("device_name_id"))

    id = Column(Integer, primary_key=True)
    remote_name = Column(String)
    online = Column(Boolean, default=False)
    reboots = Column(Integer, default=0)

    client_id = Column(ForeignKey("clients.id"))
    client = relationship("Client", uselist=False, back_populates="device")

    device_name_id = Column(ForeignKey("device_names.id"))
    device_name = relationship("DeviceName", uselist=False, back_populates="device")

    device_type_id = Column(Integer, ForeignKey("device_types.id"))
    device_type = relationship("DeviceType", back_populates="devices")

    def __init__(self, *args, client: Client, device_name: DeviceName, **kwargs):
        excs = []
        if client.device is not None:
            excs.append(DeviceClientError(client=client))

        if device_name.device is not None:
            excs.append(DeviceNameError(device_name=device_name))

        if excs:
            raise SQLAlchemyError(excs)

        super().__init__(*args, **kwargs | dict(client=client, device_name=device_name))

    def __str__(self):
        """Return ModelStrFormatter.__str__ result of both the Device object and
        its corresponding DeviceType object."""
        attrs = [
            super().__str__(),
            str(self.device_name),
            str(self.client),
            str(self.device_type),
        ]
        return "\n".join(attrs)

    class Config:
        from_attributes = True
