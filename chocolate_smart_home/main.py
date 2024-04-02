import os

from fastapi import FastAPI

from chocolate_smart_home.mqtt.client import MQTTClient
from chocolate_smart_home.routers import frontend

app = FastAPI()

app.include_router(frontend.router)

mqtt_client = MQTTClient(host=os.environ.get("MQTT_HOST", "127.0.0.1"))
mqtt_client.connect()
