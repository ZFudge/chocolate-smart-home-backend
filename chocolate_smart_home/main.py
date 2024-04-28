import os

from fastapi import FastAPI

from chocolate_smart_home.mqtt import mqtt_client_ctx
from chocolate_smart_home.routers import frontend

app = FastAPI()

app.include_router(frontend.router)

mqtt_client_ctx.get().connect()
