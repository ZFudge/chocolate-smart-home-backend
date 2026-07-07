from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    JSON,
    String,
    Table,
    Unicode,
)
from sqlalchemy.orm import relationship, Mapped

from src.database import Base


job_devices = Table(
    "job_devices",
    Base.metadata,
    Column("mqtt_id", ForeignKey("devices.mqtt_id"), primary_key=True),
    Column(
        "apscheduler_jobs_non_serializable_id",
        ForeignKey("apscheduler_jobs_non_serializable.job_id"),
        primary_key=True,
    ),
)


class ApschedulerJobsNonSerializable(Base):
    __tablename__ = "apscheduler_jobs_non_serializable"
    job_id = Column(Unicode(191), primary_key=True)
    # custom fields
    name = Column(String)
    device_type_id = Column(Integer, ForeignKey("device_types.id"))
    devices: Mapped[list[Device]] = relationship(secondary=job_devices)  # noqa: F821
    # schedulable message data
    message_kvp = Column(JSON)
    scheduler_kwargs = Column(JSON)
    active = Column(Boolean, default=True)
