from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from chocolate_smart_home.database import Base


class Space(Base):
    __tablename__ = "spaces"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)


class DeviceType(Base):
    __tablename__ = "device_types"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    devices = relationship("Device", back_populates="device_type")

    def __str__(self):
        return f'DeviceType(name="{self.name}")'

    def __repr__(self):
        return str(self)


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    mqtt_id = Column(Integer, unique=True, index=True)
    name = Column(String, unique=True)
    remote_name = Column(String)
    online = Column(Boolean, default=False)

    device_type_id = Column(Integer, ForeignKey("device_types.id"))
    device_type = relationship("DeviceType", back_populates="devices")

    def __str__(self):
        return (f"Device(mqtt_id={self.mqtt_id}, "
                       f'name="{self.name}", '
                       f'remote_name="{self.remote_name}", '
                       f"device_type={self.device_type})")

    def __repr__(self):
        return str(self)

    class Config:
        from_attributes = True
