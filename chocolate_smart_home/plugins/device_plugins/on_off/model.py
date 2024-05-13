from sqlalchemy import Boolean, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from chocolate_smart_home.database import Base, engine


class OnOffDevice(Base):
    __tablename__ = "on_off_devices"

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    device = relationship("Device")

    on = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)
