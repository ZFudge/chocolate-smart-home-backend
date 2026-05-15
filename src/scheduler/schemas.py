from pydantic import BaseModel


class Schedule(BaseModel):
    trigger: str
    cron: str = None
    dt: str = None


class MQTTIds(BaseModel):
    mqtt_ids: list[int] | None


class Job(MQTTIds):
    job_id: str
    message: dict
    schedule: Schedule


class NewJob(MQTTIds):
    job_id: str
    message: dict
    schedule: Schedule


class PatchJob(MQTTIds):
    job_id: str
    message: dict
