import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from src.redis_streams_handler import RedisStreamsHandlerCSMBackend
from src.routers import APP_ROUTERS
from src.mqtt.context import get_mqtt_client

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    mqtt_client = get_mqtt_client()
    while not mqtt_client.is_connected():
        logger.info("Waiting for the initial MQTT client connection...")
        await asyncio.sleep(3)
        mqtt_client.connect()

    asyncio.create_task(RedisStreamsHandlerCSMBackend().handle_reads())
    yield


app = FastAPI(lifespan=lifespan)

logger.info("Including routers...")
for router in APP_ROUTERS:
    app.include_router(router)
