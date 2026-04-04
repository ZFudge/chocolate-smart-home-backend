import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from src.redis_streams_handler import RedisStreamsHandlerCSMBackend
from src.routers import APP_ROUTERS

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(RedisStreamsHandlerCSMBackend().handle_reads())
    yield


app = FastAPI(lifespan=lifespan)

logger.info("Including routers...")
for router in APP_ROUTERS:
    app.include_router(router)
