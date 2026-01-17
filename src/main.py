import logging

from fastapi import FastAPI

from src.mqtt import get_mqtt_client
from src.plugins.discovered_plugins import (
    PLUGIN_ROUTERS,
    discover_and_import_device_plugin_modules,
)
from src.routers import APP_ROUTERS

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = FastAPI()

mqtt_client = get_mqtt_client()

# Wait for the MQTT client to connect
while not mqtt_client.is_connected():
    logger.info("Waiting for the initial MQTT client connection...")
    mqtt_client.connect()

# Plugin modules import the MQTT client context, and the MQTT message handler
# imports plugins, so plugin module imports are deferred until after the MQTT
# client is connected and its context is set.
discover_and_import_device_plugin_modules()

logger.info("Including routers...")
# With plugins imported, their endpoints can be included.
for router in APP_ROUTERS + tuple(PLUGIN_ROUTERS):
    app.include_router(router)
