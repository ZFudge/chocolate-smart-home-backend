from fastapi import FastAPI
from chocolate_smart_home.mqtt import get_mqtt_client

from chocolate_smart_home.plugins.discovered_plugins import (
    PLUGIN_ROUTERS,
    discover_and_import_device_plugin_modules,
)
from chocolate_smart_home.routers import APP_ROUTERS


app = FastAPI()

client = get_mqtt_client()
if client is not None:
    client.connect()

# Plugin modules import the MQTT client context, and the MQTT message handler
# imports plugins, so plugin module imports are deferred until after the MQTT
# client is connected and its context is set.
discover_and_import_device_plugin_modules()

# With plugins imported, their endpoints can be included.
for router in APP_ROUTERS + tuple(PLUGIN_ROUTERS):
    app.include_router(router)
