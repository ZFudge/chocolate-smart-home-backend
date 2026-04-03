from typing import List

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Mapped

from src.database import Base
from .device_tags import device_tags
from .tag import Tag


class Device(Base):
    __tablename__ = "devices"

    mqtt_id = Column(Integer, primary_key=True)

    last_seen = Column(DateTime, default=None)
    last_update_sent = Column(DateTime, default=None)
    reboots = Column(Integer, default=0)

    remote_name = Column(String)
    name = Column(String)

    device_type_id = Column(Integer, ForeignKey("device_types.id"))
    device_type = relationship("DeviceType", back_populates="devices")

    tags: Mapped[List[Tag]] = relationship(
        secondary=device_tags, back_populates="devices"
    )

    def __str__(self):
        return (
            f"Device("
            f"mqtt_id={self.mqtt_id}, "
            f"last_seen={self.last_seen}, "
            f"last_update_sent={self.last_update_sent}, "
            f"reboots={self.reboots}, "
            f"remote_name={self.remote_name}, "
            f"name={self.name}, "
            f"device_type_name={self.device_type.name}, "
            f'tags={(f'[{", ".join([tag.name for tag in self.tags])}]') if self.tags else "null"})'
        )

    def __repr__(self):
        return str(self)

    class Config:
        from_attributes = True
