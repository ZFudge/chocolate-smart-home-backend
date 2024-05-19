from fastapi import APIRouter

from chocolate_smart_home.mqtt import topics, mqtt_client_ctx
from .duplex_messenger import DuplexMessenger


plugin_router = APIRouter(prefix="/on_off")
SEND_TOPIC_TMPT = topics.SEND_DEVICE_DATA_TEMPLATE.format(device_type="on_off")

@plugin_router.patch("{device_id}/{on_off}", response_model=None, status_code=204)
def on_off(device_id: int, on_off: bool):
    topic: str = SEND_TOPIC_TMPT.format(device_id=device_id)
    outgoing_msg: str = DuplexMessenger().compose_msg(on_off)
    mqtt_client_ctx.get().publish(topic, outgoing_msg)
