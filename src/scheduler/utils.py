from apscheduler.job import Job


def serialize_job(job: Job) -> dict:
    return {
        "id": job.id,
        "name": job.name,
        "trigger": dict([(f.name, f) for f in job.trigger.fields if not f.is_default]),
    }
