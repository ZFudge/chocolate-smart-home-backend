from sqlalchemy import Boolean, Column, Integer, String

from chocolate_smart_home.database import Base
from .model_str_formatter import ModelStrFormatter


class DeviceName(Base, ModelStrFormatter):
    __tablename__ = "device_names"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    is_server_side_name = Column(Boolean, default=False)
