from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from chocolate_smart_home.database import Base
from .model_str_formatter import ModelStrFormatter


class Device(Base, ModelStrFormatter):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    mqtt_id = Column(Integer, unique=True)

    online = Column(Boolean, default=False)
    reboots = Column(Integer, default=0)

    remote_name = Column(String)
    name = Column(String)

    device_type_id = Column(Integer, ForeignKey("device_types.id"))
    device_type = relationship("DeviceType", back_populates="devices")

    tag_id = Column(Integer, ForeignKey("tags.id"))
    tag = relationship("Tag", back_populates="devices")

    def __str__(self):
        """Return ModelStrFormatter.__str__ result of both the Device object and
        its corresponding DeviceType object."""
        attrs = [
            super().__str__(),
            str(self.device_type),
            str(self.tag) if self.tag else "Tag=None",
        ]
        return "\n".join(attrs)

    class Config:
        from_attributes = True
