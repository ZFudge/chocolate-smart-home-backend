from typing import Any

from pydantic import BaseModel


class MQTTIds(BaseModel):
    mqtt_ids: list[int]


class JobId(BaseModel):
    job_id: str


class JobName(BaseModel):
    name: str


class KVP(BaseModel):
    key: str = None
    value: Any = None


class MessageKVP(BaseModel):
    message_kvp: KVP


class SchedulerKwargs(BaseModel):
    scheduler_kwargs: dict[str, Any]


class JobToSchedule(MQTTIds, MessageKVP, SchedulerKwargs):
    job_id: str = None
    name: str = None
    device_type_name: str
    active: bool = True


class JobResponse(JobId, MQTTIds, JobName, MessageKVP, SchedulerKwargs):
    device_type_id: int
    active: bool = True


class ModifyJob(BaseModel):
    name: str = None
    mqtt_ids: list[int] = None
    message_kvp: KVP = None
    scheduler_kwargs: dict[str, Any] = None
    active: bool = None
