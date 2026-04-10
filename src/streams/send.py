import json
import logging

from . import stream_names
from src.dependencies import redis_session
from src.schemas import DeviceFrontend as DeviceFrontendSchema

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def send_to_ws_service(device_data: DeviceFrontendSchema):
    data = device_data.model_dump()
    message_data = dict(message=json.dumps(data))
    await redis_session.get().xadd(stream_names.WS_STREAM_NAME, message_data)
