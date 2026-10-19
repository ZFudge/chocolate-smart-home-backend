import asyncio
import datetime as dt
import logging
import os
import random

from astral import LocationInfo
from astral.sun import sun

from src.dependencies import asyncio_event_loop, db_session, redis_session
from src.scheduler import scheduler

from .Model import PluginModel as NeoPixel
from .models import Palette

logger = logging.getLogger("scheduler")

BACKEND_STREAM_NAME = os.getenv("BACKEND_STREAM_NAME")
LATITUDE = float(os.getenv("LATITUDE"))
LONGITUDE = float(os.getenv("LONGITUDE"))
TZ = os.getenv("TZ")


def turn_on_automatic_lights():
    logger.info("Turning on all NeoPixels")
    if db_session is None:
        raise ValueError("Database session not initialized")
    if redis_session is None:
        raise ValueError("Redis session not initialized")
    if asyncio_event_loop is None:
        raise ValueError("Asyncio event loop not initialized")
    neo_pixel_devices = db_session.query(NeoPixel).all()
    if len(neo_pixel_devices) == 0:
        return
    mqtt_ids: list[int] = [d.mqtt_id for d in neo_pixel_devices]
    message_data = {
        "mqtt_id": str(mqtt_ids),
        "device_type_name": "neo_pixel",
        "name": "on",
        "value": "True",
    }
    asyncio.run_coroutine_threadsafe(
        redis_session.xadd(
            BACKEND_STREAM_NAME,
            message_data,
        ),
        asyncio_event_loop,
    )


def schedule_lights_before_sunset_by_location():
    logger.info("Scheduling lights on, before sunset, by location.")
    location = LocationInfo(
        timezone=TZ,
        latitude=LATITUDE,
        longitude=LONGITUDE,
    )
    sun_data = sun(location.observer, date=dt.date.today(), tzinfo=TZ)
    sunset_time = sun_data["sunset"]
    lights_on_time = sunset_time - dt.timedelta(minutes=30)
    scheduler.add_job(
        turn_on_automatic_lights,
        id="turn_on_automatic_lights",
        jobstore="default",
        replace_existing=True,
        trigger="interval",
        start_date=lights_on_time,
        days=1,
    )
    logger.info(f"Scheduled lights on at {lights_on_time}")


def rotate_palette():
    logger.info("Checking NeoPixel palette rotation")
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
        d.all_twinkle_colors_are_current is True for d in scheduled_devices
    ):
        logger.info(
            "No scheduled devices or all twinkle colors are not current, skipping palette rotation"
        )
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
    logger.info(f"Sending palette rotation message: {message_data}")
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
        "trigger": "cron",
        "minute": "*/3",
    },
    {
        "func": schedule_lights_before_sunset_by_location,
        "id": "neo_pixel_schedule_lights_before_sunset",
        "trigger": "cron",
        "hour": "*",
    },
)
