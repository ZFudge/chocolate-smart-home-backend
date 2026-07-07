import logging

from apscheduler.job import Job
from fastapi import APIRouter, HTTPException

from . import crud, model, schemas

scheduler_router = APIRouter(prefix="/scheduler")

logger = logging.getLogger("scheduler")


@scheduler_router.get("/")
def get_jobs():
    try:
        jobs: list[model.ApschedulerJobsNonSerializable | Job] = crud.get_jobs()
        return tuple(map(crud.serialize_job, jobs))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=500, detail="Error broadcasting request for devices state."
        )


@scheduler_router.get("/{job_id}")
def get_job(job_id: str):
    try:
        job: model.ApschedulerJobsNonSerializable | Job | None = crud.get_job_by_id(
            job_id
        )
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=500, detail="Error getting scheduled job with id %s." % job_id
        )
    if job is None:
        raise HTTPException(
            status_code=404, detail="Job with id %s not found." % job_id
        )
    return crud.serialize_job(job)


@scheduler_router.post("/", response_model=schemas.JobResponse)
def create_job(new_job: schemas.JobToSchedule):
    try:
        job: model.ApschedulerJobsNonSerializable = crud.create_job(new_job)
        return crud.serialize_job(job)
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=500,
            detail="Error creating scheduled job with id",
        )


@scheduler_router.delete("/{job_id}", response_model=None, status_code=204)
def delete_job(job_id: str):
    try:
        crud.delete_job_by_id(job_id)
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=500, detail="Error deleting scheduled job with id %s." % job_id
        )


@scheduler_router.patch("/{job_id}", response_model=schemas.JobResponse)
def modify_job(job_id: str, modified_job: schemas.ModifyJob):
    try:
        job: model.ApschedulerJobsNonSerializable | None = crud.modify_job_by_id(
            job_id, modified_job
        )
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=500, detail="Error modifying scheduled job with id %s." % job_id
        )
    if job is None:
        raise HTTPException(
            status_code=404, detail="Job with id %s not found." % job_id
        )
    return crud.serialize_job(job)
