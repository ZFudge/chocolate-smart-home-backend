from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY


class Palette:
    __tablename__ = "palettes"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    colors = Column(ARRAY(String), unique=True)


models = (Palette,)
