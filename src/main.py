import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.dependencies import mqtt_client_session
from src.plugins.discovered_plugins import discover_and_import_device_plugin_modules
from src.pubsub.connect import connect_to_mqtt_broker
from src.pubsub.handler import mqtt_message_handler
from src.pubsub.publish import subscribe
from src.pubsub.topics import RECEIVE_DEVICE_DATA
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
        subscribe(RECEIVE_DEVICE_DATA, mqtt_message_handler)

    asyncio.create_task(RedisStreamsHandlerCSMBackend().handle_reads())
    yield


app = FastAPI(lifespan=lifespan)

# Plugin modules import the MQTT client context, and the MQTT message handler
# imports plugins, so plugin module imports are deferred until after the MQTT
# client is connected and its context is set.
discover_and_import_device_plugin_modules()

logger.info("Including routers...")
for router in APP_ROUTERS:
    app.include_router(router)
