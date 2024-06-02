from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from chocolate_smart_home.database import Base
from .model_str_formatter import ModelStrFormatter


class Client(Base, ModelStrFormatter):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    mqtt_id = Column(Integer, unique=True)
