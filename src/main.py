import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.dependencies import mqtt_client_session
from src.plugins import discovered_plugins
from src.pubsub import connect_to_mqtt_broker, subscribe, topics
from src.pubsub.handler import mqtt_message_handler
from src.redis_streams_handler import RedisStreamsHandlerCSMBackend
from src.routers import APP_ROUTERS

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    mqtt_client = mqtt_client_session.get()
    while not mqtt_client.is_connected():
        logger.info("Waiting for the initial MQTT client connection...")
        await asyncio.sleep(3)
        connect_to_mqtt_broker()
        subscribe(topic=topics.RECEIVE_DEVICE_DATA, handler=mqtt_message_handler)
    asyncio.create_task(RedisStreamsHandlerCSMBackend().handle_reads())
    yield


app = FastAPI(lifespan=lifespan)


discovered_plugins.discover_and_import_device_plugin_modules()

logger.info("Including routers...")
for router in APP_ROUTERS:
    app.include_router(router)
