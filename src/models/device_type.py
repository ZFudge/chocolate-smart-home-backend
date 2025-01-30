from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.database import Base
from .model_str_formatter import ModelStrFormatter


class DeviceType(Base, ModelStrFormatter):
    __tablename__ = "device_types"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    devices = relationship("Device", back_populates="device_type")
