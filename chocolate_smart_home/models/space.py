from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from chocolate_smart_home.database import Base
from .model_str_formatter import ModelStrFormatter


class Space(Base, ModelStrFormatter):
    __tablename__ = "spaces"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    devices = relationship("Device", back_populates="space")
