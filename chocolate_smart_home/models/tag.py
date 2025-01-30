from sqlalchemy import Column, Integer, String

from chocolate_smart_home.database import Base
from .model_str_formatter import ModelStrFormatter


class Tag(Base, ModelStrFormatter):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
