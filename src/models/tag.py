from __future__ import annotations
from typing import List

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, Mapped

from src.database import Base
from .device_tags import device_tags
from .model_str_formatter import ModelStrFormatter


class Tag(Base, ModelStrFormatter):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    devices: Mapped[List[Device]] = relationship(secondary=device_tags, back_populates="tags")
