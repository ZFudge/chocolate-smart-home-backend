from sqlalchemy import Column, ForeignKey, Table

from src.database import Base


device_tags = Table(
    "device_tags",
    Base.metadata,
    Column("mqtt_id", ForeignKey("devices.mqtt_id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)
