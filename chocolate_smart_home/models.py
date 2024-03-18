from sqlalchemy import Boolean, Column, Integer, String

from chocolate_smart_home.database import Base


class Space(Base):
    __tablename__ = "spaces"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    mqtt_id = Column(Integer, unique=True, index=True)
    name = Column(String, unique=True)
    remote_name = Column(String)
    online = Column(Boolean, default=False)

    class Config:
        from_attributes = True
