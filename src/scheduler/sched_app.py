import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.plugins.manager import PluginsManager
from src.scheduler.router import scheduler_router
from src.scheduler.scheduler import scheduler
from src.scheduler.crud import load_jobs_from_db

logger = logging.getLogger("scheduler")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting scheduler...")
    scheduler.start()
    load_jobs_from_db()
    yield
    logger.info("Stopping scheduler...")
    scheduler.shutdown()
    logger.info("Scheduler stopped")


PluginsManager.discover_scheduling()

sched_app = FastAPI(title="CSM Scheduler", version="0.1.0", lifespan=lifespan)
sched_app.include_router(scheduler_router)
