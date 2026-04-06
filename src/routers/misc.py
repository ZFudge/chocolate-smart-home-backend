import logging

from fastapi import APIRouter, HTTPException
from paho.mqtt import MQTTException
from src.mqtt.context import get_mqtt_client

misc_router = APIRouter()

logger = logging.getLogger(__name__)


@misc_router.head(
    "/broadcast_request_devices_state/", response_model=None, status_code=204
)
def broadcast_request_devices_state():
    try:
        get_mqtt_client().request_all_devices_data()
    except MQTTException as e:
        logger.error(e)
        raise HTTPException(
            status_code=500, detail="Error broadcasting request for devices state."
        )
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=500, detail="Error broadcasting request for devices state."
        )
