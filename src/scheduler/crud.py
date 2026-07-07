import logging
import os

from apscheduler.job import Job
from apscheduler.jobstores.base import JobLookupError

from src.crud.device_types import get_device_type_by_name, get_device_type_by_id
from src.crud.utils import commit_db_object
from src.dependencies import db_session, redis_session
from src import models
from . import model, schemas
from .scheduler import scheduler as sched

logger = logging.getLogger("scheduler")


BACKEND_STREAM_NAME = os.getenv("BACKEND_STREAM_NAME")


def serialize_job(job: model.ApschedulerJobsNonSerializable) -> dict:
    if isinstance(job, model.ApschedulerJobsNonSerializable):
        return schemas.JobResponse(
            job_id=job.job_id,
            name=job.name,
            device_type_id=job.device_type_id,
            mqtt_ids=[device.mqtt_id for device in job.devices],
            message_kvp=schemas.KVP(
                key=job.message_kvp["key"], value=job.message_kvp["value"]
            ),
            scheduler_kwargs=job.scheduler_kwargs,
            active=job.active,
        )


def schedule_memory_job(job: schemas.JobToSchedule) -> Job:
    message = {
        "device_type_name": job.device_type_name,
        "mqtt_ids": job.mqtt_ids,
        "key": job.message_kvp.key,
        "value": job.message_kvp.value,
    }

    def func():
        redis_session.xadd(
            BACKEND_STREAM_NAME,
            message,
        )

    scheduled_job = sched.add_job(
        func,
        id=job.job_id,
        jobstore="default",
        replace_existing=True,
        **job.scheduler_kwargs,  # type: ignore
    )

    return scheduled_job


def schedule_job_from_db_obj(db_job: model.ApschedulerJobsNonSerializable) -> None:
    device_type = get_device_type_by_id(db_job.device_type_id)
    job_data = schemas.JobToSchedule(
        job_id=db_job.job_id,
        device_type_name=device_type.name,
        mqtt_ids=[d.mqtt_id for d in db_job.devices],
        message_kvp=schemas.KVP(
            key=db_job.message_kvp["key"],
            value=db_job.message_kvp["value"],
        ),
        scheduler_kwargs=db_job.scheduler_kwargs,
        active=db_job.active,
    )
    schedule_memory_job(job_data)


def load_jobs_from_db():
    jobs = db_session.get().query(model.ApschedulerJobsNonSerializable).all()
    for job in jobs:
        schedule_job_from_db_obj(job)


def create_job(new_job: schemas.JobToSchedule) -> model.ApschedulerJobsNonSerializable:
    device_type = get_device_type_by_name(new_job.device_type_name)
    if device_type is None:
        raise ValueError(f"Device type {new_job.device_type_name} not found")
    devices = (
        db_session.get()
        .query(models.Device)
        .where(models.Device.mqtt_id.in_(new_job.mqtt_ids))
        .all()
    )
    if len(devices) != len(new_job.mqtt_ids):
        unknown_mqtt_ids = set(new_job.mqtt_ids) - set(
            device.mqtt_id for device in devices
        )
        raise ValueError(f"Devices {unknown_mqtt_ids} not found")

    created_job = schedule_memory_job(new_job)
    if new_job.active is False:
        sched.pause_job(created_job.id)
    new_db_job = model.ApschedulerJobsNonSerializable(
        job_id=created_job.id,
        name=new_job.name,
        device_type_id=device_type.id,
        devices=devices,
        message_kvp=dict(key=new_job.message_kvp.key, value=new_job.message_kvp.value),
        scheduler_kwargs=new_job.scheduler_kwargs,
        active=new_job.active,
    )
    committed_new_db_job = commit_db_object(new_db_job)
    return committed_new_db_job


def get_job_by_id_from_db(job_id: str) -> model.ApschedulerJobsNonSerializable | None:
    job = (
        db_session.get()
        .query(model.ApschedulerJobsNonSerializable)
        .where(model.ApschedulerJobsNonSerializable.job_id == job_id)
        .one_or_none()
    )
    return job


def get_job_by_id(job_id: str) -> model.ApschedulerJobsNonSerializable | Job | None:
    job = get_job_by_id_from_db(job_id)
    if job is None:
        try:
            job = sched.get_job(job_id)
        except JobLookupError as e:
            logger.warning(f"Job {job_id} not found in scheduler: {e}")
            return None
    return job


def get_jobs() -> list[model.ApschedulerJobsNonSerializable | Job]:
    jobs = db_session.get().query(model.ApschedulerJobsNonSerializable).all()
    return jobs


def delete_job_by_id(job_id: str) -> None:
    try:
        sched.remove_job(job_id)
    except JobLookupError as e:
        logger.warning(f"Job {job_id} not found in scheduler: {e}")
    job = get_job_by_id_from_db(job_id)
    if job is None:
        logger.warning(f"Job {job_id} not found in database")
        return
    db = db_session.get()
    db.delete(job)
    db.commit()


def modify_job_by_id(
    job_id: str, modified_job: schemas.ModifyJob
) -> model.ApschedulerJobsNonSerializable | None:
    job = get_job_by_id_from_db(job_id)
    if job is None:
        logger.warning(f"Job {job_id} not found in database")
        return
    reschedule = True
    if modified_job.active is not None:
        if modified_job.active:
            sched.resume_job(job_id)
        else:
            sched.pause_job(job_id)
        job.active = modified_job.active
    if modified_job.message_kvp is not None:
        job.message_kvp = dict(
            key=modified_job.message_kvp.key, value=modified_job.message_kvp.value
        )
    if modified_job.scheduler_kwargs is not None:
        job.scheduler_kwargs = modified_job.scheduler_kwargs
    if reschedule:
        device_type = get_device_type_by_id(job.device_type_id)
        job_to_schedule = schemas.JobToSchedule(
            job_id=job_id,
            device_type_name=device_type.name,
            mqtt_ids=modified_job.mqtt_ids or [d.mqtt_id for d in job.devices],
            message_kvp=schemas.KVP(
                key=(
                    modified_job.message_kvp.key
                    if modified_job.message_kvp is not None
                    else job.message_kvp["key"]
                ),
                value=(
                    modified_job.message_kvp.value
                    if modified_job.message_kvp is not None
                    else job.message_kvp["value"]
                ),
            ),
            scheduler_kwargs=(
                modified_job.scheduler_kwargs
                if modified_job.scheduler_kwargs is not None
                else job.scheduler_kwargs
            ),
        )
        schedule_memory_job(job_to_schedule)
    committed_job = commit_db_object(job)
    return committed_job
