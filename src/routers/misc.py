from fastapi import APIRouter, HTTPException
from paho.mqtt import MQTTException
from src.mqtt.context import get_mqtt_client

misc_router = APIRouter()


@misc_router.head(
    "/broadcast_request_devices_state/", response_model=None, status_code=204
)
def broadcast_request_devices_state():
    try:
        get_mqtt_client().request_all_devices_data()
    except MQTTException as e:
        (detail,) = e.args
        raise HTTPException(status_code=500, detail=detail)
