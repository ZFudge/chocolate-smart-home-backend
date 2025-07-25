from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from src.database import Base, engine
from src.plugins.plugin_model_string_formatter import (
    PluginModelStrFormatter,
)


class NeoPixel(Base, PluginModelStrFormatter):
    __tablename__ = "neo_pixel_devices"

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    device = relationship("Device")

    on = Column(Boolean)
    twinkle = Column(Boolean)
    all_twinkle_colors_are_current = Column(Boolean, nullable=True)
    scheduled_palette_rotation = Column(Boolean)
    transform = Column(Boolean)
    ms = Column(Integer)
    brightness = Column(Integer)

    palette = Column(ARRAY(String))

    armed = Column(Boolean, nullable=True)
    timeout = Column(Integer, nullable=True)


Base.metadata.create_all(bind=engine)
