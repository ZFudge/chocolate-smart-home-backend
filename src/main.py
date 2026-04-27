import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.dependencies import mqtt_client_session
from src.plugins import PluginsManager
from src.pubsub import connect_to_mqtt_broker, subscribe, topics
from src.pubsub.handler import mqtt_message_handler
from src.routers import APP_ROUTERS
from src.streams import handle_reads as handle_redis_stream_reads

logger = logging.getLogger(__name__)


class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return "/healthcheck" not in record.getMessage()


logging.getLogger("uvicorn.access").addFilter(EndpointFilter())


@asynccontextmanager
async def lifespan(app: FastAPI):
    mqtt_client = mqtt_client_session.get()
    while not mqtt_client.is_connected():
        logger.info("Waiting for the initial MQTT client connection...")
        await asyncio.sleep(3)
        connect_to_mqtt_broker()
    subscribe(topic=topics.RECEIVE_DEVICE_DATA, handler=mqtt_message_handler)
    asyncio.create_task(handle_redis_stream_reads())
    yield


app = FastAPI(lifespan=lifespan)

PluginsManager.discover_plugins()

logger.info("Including routers...")
for router in APP_ROUTERS + tuple(PluginsManager.ROUTERS):
    app.include_router(router)
