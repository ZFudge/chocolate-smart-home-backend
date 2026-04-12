import logging

from fastapi import APIRouter, HTTPException

from src.dependencies import db_session, mqtt_client_session
from src.pubsub import request_all_devices_data

# from src.redis_streams_handler import RedisStreamsHandlerCSMBackend

misc_router = APIRouter()

logger = logging.getLogger(__name__)


@misc_router.head(
    "/broadcast_request_devices_state/", response_model=None, status_code=204
)
def broadcast_request_devices_state():
    try:
        request_all_devices_data()
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=500, detail="Error broadcasting request for devices state."
        )


@misc_router.get("/healthcheck")
def health_check():
    if (
        not mqtt_client_session.get().is_connected()
        # or not RedisStreamsHandlerCSMBackend().is_connected()
        or not db_session.get().is_active
    ):
        raise HTTPException(status_code=500)
