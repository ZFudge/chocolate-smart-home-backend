from datetime import datetime


from sqlalchemy import Column, DateTime, func, Integer, String


class Properties:
    __tablename__ = "properties"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    value = Column(String, nullable=True)


class Readings:
    __tablename__ = "readings"
    id = Column(Integer, primary_key=True)
    reading = Column(String, unique=True)
    date = Column[datetime](DateTime, default=func.now())


models = (Properties, Readings)
