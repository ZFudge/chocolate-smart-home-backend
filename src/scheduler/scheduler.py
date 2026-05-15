import logging

from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.job import Job
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc

from src import database

logger = logging.getLogger("scheduler")


scheduler = AsyncIOScheduler()

scheduler.configure(
    jobstores={
        "default": MemoryJobStore(),
        "sql": SQLAlchemyJobStore(url=database.get_sqlalchemy_database_url()),
    },
    executors={
        "default": ThreadPoolExecutor(20),
        "processpool": ProcessPoolExecutor(5),
    },
    job_defaults={"coalesce": False, "max_instances": 3},
    timezone=utc,
)


def add_job(func: callable, **kwargs) -> Job:
    logger.info(f"{scheduler=} Adding job {func=} with {kwargs=}")
    new_job: Job = scheduler.add_job(
        func,
        trigger="cron",
        jobstore="sql",
        replace_existing=True,
        **kwargs,
    )
    return new_job
