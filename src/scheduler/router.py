import logging

from apscheduler.job import Job
from fastapi import APIRouter, HTTPException

from . import schemas
from .scheduler import scheduler as sched, add_job
from .utils import serialize_job

scheduler_router = APIRouter(prefix="/scheduler")

logger = logging.getLogger("scheduler")


@scheduler_router.get("/jobs")
def get_jobs():
    try:
        jobs: list[Job] = sched.get_jobs("sql")
        return tuple(map(serialize_job, jobs))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=500, detail="Error broadcasting request for devices state."
        )


@scheduler_router.get("/job/{job_id}")
def get_job(job_id: str):
    try:
        job: Job = sched.get_job(job_id, "sql")
        return serialize_job(job)
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=500, detail="Error getting scheduled job with id %s." % job_id
        )


@scheduler_router.post("/job")
def create_job(job: schemas.NewJob):
    try:
        job = add_job(
            job.message, job.schedule.trigger, jobstore="sql", **job.schedule.kwargs
        )
        return serialize_job(job)
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=500,
            detail="Error creating scheduled job with id %s." % job.job_id,
        )


@scheduler_router.patch("/job/{job_id}")
def patch_job(job: schemas.PatchJob):
    try:
        job = sched.modify_job(
            job.job_id, job.schedule.trigger, jobstore="sql", **job.schedule.kwargs
        )
        return serialize_job(job)
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=500,
            detail="Error patching scheduled job with id %s." % job.job_id,
        )


@scheduler_router.delete("/job/{job_id}", response_model=None, status_code=204)
def delete_job(job_id: str):
    try:
        sched.remove_job(job_id, jobstore="sql")
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=500, detail="Error deleting scheduled job with id %s." % job_id
        )
