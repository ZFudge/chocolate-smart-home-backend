from fastapi import FastAPI

from src.mqtt import get_mqtt_client
from src.plugins.discovered_plugins import (
    PLUGIN_ROUTERS,
    discover_and_import_device_plugin_modules,
)
from src.routers import APP_ROUTERS


app = FastAPI()

mqtt_client = get_mqtt_client()
if mqtt_client is not None:
    mqtt_client.connect()

# Plugin modules import the MQTT client context, and the MQTT message handler
# imports plugins, so plugin module imports are deferred until after the MQTT
# client is connected and its context is set.
discover_and_import_device_plugin_modules()

# With plugins imported, their endpoints can be included.
for router in APP_ROUTERS + tuple(PLUGIN_ROUTERS):
    app.include_router(router)
