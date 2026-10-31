import logging

from fastapi import APIRouter, HTTPException

from src.dependencies import (
    db_session,
    mqtt_client_session,
)
from src.pubsub import request_all_devices_data
from src.utils import get_request_all_device_data_last_sent_as_dt

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
        last_sent_dt = await get_request_all_device_data_last_sent_as_dt()
        return (
            last_sent_dt.astimezone() if isinstance(last_sent_dt, dt.datetime) else None
        )
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
