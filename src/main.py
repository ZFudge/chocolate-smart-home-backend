import logging

from fastapi import FastAPI
from src.routers import APP_ROUTERS

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = FastAPI()

logger.info("Including routers...")
for router in APP_ROUTERS:
    app.include_router(router)
