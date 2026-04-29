from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY


class PluginModel:
    __tablename__ = "neo_pixel"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True)

    on = Column(Boolean)
    twinkle = Column(Boolean)
    all_twinkle_colors_are_current = Column(Boolean, nullable=True)
    scheduled_palette_rotation = Column(Boolean, default=False)
    transform = Column(Boolean)
    ms = Column(Integer)
    brightness = Column(Integer)

    palette = Column(ARRAY(String))

    pir_enabled = Column(Boolean, nullable=True, default=False)
    pir_armed = Column(Boolean, nullable=True)
    pir_timeout = Column(Integer, nullable=True)
