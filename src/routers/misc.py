import datetime as dt
import logging

from fastapi import APIRouter, HTTPException

from src.dependencies import db_session, mqtt_client_session, redis_session
from src.pubsub import request_all_devices_data

misc_router = APIRouter()

logger = logging.getLogger(__name__)


@misc_router.head(
    "/broadcast_request_devices_state/", response_model=None, status_code=204
)
async def broadcast_request_devices_state():
    try:
        request_all_devices_data()
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=500, detail="Error broadcasting request for devices state."
        )


@misc_router.get(
    "/request_all_device_data_last_sent/",
)
async def request_all_device_data_last_sent():
    try:
        request_all_device_data_last_sent = await redis_session.get().get(
            "request_all_device_data_last_sent"
        )
        request_all_device_data_last_sent_dt = dt.datetime.fromtimestamp(
            int(request_all_device_data_last_sent)
        )
        return request_all_device_data_last_sent_dt.astimezone()
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=500, detail="Error broadcasting request for devices state."
        )


@misc_router.get("/healthcheck")
def health_check():
    if (
        not mqtt_client_session.get().is_connected()
        # TODO: add redis healthcheck
        or not db_session.get().is_active
    ):
        raise HTTPException(status_code=500)
