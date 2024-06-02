from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from chocolate_smart_home.database import Base
from .model_str_formatter import ModelStrFormatter


class Device(Base, ModelStrFormatter):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    remote_name = Column(String)
    online = Column(Boolean, default=False)
    reboots = Column(Integer, default=0)

    client_id = Column(Integer, ForeignKey("clients.id"))
    client = relationship("Client", uselist=False, backref="device")

    device_type_id = Column(Integer, ForeignKey("device_types.id"))
    device_type = relationship("DeviceType", back_populates="devices")

    device_name_id = Column(Integer, ForeignKey("device_names.id"))
    device_name = relationship("DeviceName", uselist=False, backref="devices")

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
