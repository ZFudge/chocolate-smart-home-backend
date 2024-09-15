from sqlalchemy import Boolean, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from chocolate_smart_home.database import Base, engine
from chocolate_smart_home.plugins.plugin_model_string_formatter import (
    PluginModelStrFormatter,
)


class NeoPixel(Base, PluginModelStrFormatter):
    __tablename__ = "neo_pixel_devices"

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    device = relationship("Device")

    on = Column(Boolean, default=False)


Base.metadata.create_all(bind=engine)
