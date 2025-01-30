from sqlalchemy import Column, ForeignKey, Integer

from src.database import Base


class DeviceTag(Base):
    __tablename__ = "devices_tags"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    tag_id = Column(Integer, ForeignKey("tags.id"))
