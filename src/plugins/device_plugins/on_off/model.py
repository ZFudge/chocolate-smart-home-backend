from sqlalchemy import Boolean, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from src.database import Base, engine
from src.plugins.plugin_model_string_formatter import (
    PluginModelStrFormatter,
)


class OnOff(Base, PluginModelStrFormatter):
    __tablename__ = "on_off_devices"

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    device = relationship("Device")

    on = Column(Boolean, default=False)


try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(e)
    print("Error creating tables")
    print("Continuing...")
