from typing import List

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Mapped

from src.database import Base
from .device_tags import device_tags
from .model_str_formatter import ModelStrFormatter
from .tag import Tag


class Device(Base, ModelStrFormatter):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    mqtt_id = Column(Integer, unique=True)

    online = Column(Boolean, default=False)
    last_seen = Column(DateTime, default=None)
    reboots = Column(Integer, default=0)

    remote_name = Column(String)
    name = Column(String)

    device_type_id = Column(Integer, ForeignKey("device_types.id"))
    device_type = relationship("DeviceType", back_populates="devices")

    tags: Mapped[List[Tag]] = relationship(secondary=device_tags, back_populates="devices")

    def __str__(self):
        """Return ModelStrFormatter.__str__ result of both the Device object and
        its corresponding DeviceType object."""
        attrs = [
            super().__str__(),
            str(self.device_type),
            str(self.tags) if self.tags else "Tag=None",
        ]
        return "\n".join(attrs)

    class Config:
        from_attributes = True
