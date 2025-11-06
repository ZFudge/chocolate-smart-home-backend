from fastapi import APIRouter, HTTPException

from .crud import publish_message
from .duplex_messenger import LeonardoDuplexMessenger

plugin_router = APIRouter(prefix="/leonardo")


@plugin_router.post(
    "/{leonardo_device_id}/{command}", response_model=None, status_code=204
)
def update_device(leonardo_device_id: int, command: str):
    """Publish new message to Leonardo controller."""
    try:
        # Validate message
        LeonardoDuplexMessenger().compose_msg(command)
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    publish_message(leonardo_device_id=leonardo_device_id, command=command)
