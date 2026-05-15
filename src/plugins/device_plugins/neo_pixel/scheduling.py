import asyncio
import logging
import os
import random

from redis.asyncio import Redis
from sqlalchemy.orm import Session
from uvloop import Loop

from .Model import PluginModel as NeoPixel
from .models import Palette

logger = logging.getLogger("scheduler")

BACKEND_STREAM_NAME = os.getenv("BACKEND_STREAM_NAME")
db_session: Session | None = None
redis_session: Redis | None = None
asyncio_event_loop: Loop | None = None


def rotate_palette():
    if db_session is None:
        raise ValueError("Database session not initialized")
    if redis_session is None:
        raise ValueError("Redis session not initialized")
    if asyncio_event_loop is None:
        raise ValueError("Asyncio event loop not initialized")
    scheduled_devices = (
        db_session.query(NeoPixel)
        .where(NeoPixel.scheduled_palette_rotation.is_(True))
        .all()
    )
    if len(scheduled_devices) == 0 or not all(
        [d.all_twinkle_colors_are_current is True for d in scheduled_devices]
    ):
        return
    mqtt_ids: list[int] = [d.mqtt_id for d in scheduled_devices]
    palette_presets = db_session.query(Palette).all()
    current_palette = scheduled_devices[0].palette
    new_palette = current_palette
    while new_palette == current_palette:
        new_palette = random.choice(palette_presets).colors
    message_data = {
        "mqtt_id": str(mqtt_ids),
        "device_type_name": "neo_pixel",
        "name": "palette",
        "value": str(new_palette),
    }
    logger.info(f"Palette rotation message data: {message_data}")
    asyncio.run_coroutine_threadsafe(
        redis_session.xadd(
            BACKEND_STREAM_NAME,
            message_data,
        ),
        asyncio_event_loop,
    )


jobs = (
    {
        "func": rotate_palette,
        "id": "neo_pixel_palette_rotation",
        "minute": "*/6",
    },
)
