import logging
import os
import sys
from contextvars import ContextVar

import sqlalchemy.exc as exc
import uvloop
from paho.mqtt.client import Client
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from src.database import Base, SessionLocal, engine
from src.mqtt import get_configured_mqtt_client


logger = logging.getLogger()


try:
    Base.metadata.create_all(bind=engine)
except exc.SQLAlchemyError as e:
    if "pytest" not in sys.modules:
        logger.error(e)
        raise


def db_closure():
    db: Session | None = None

    def db_func():
        nonlocal db
        if db is None:
            db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    return db_func


get_db = db_closure()

db_session: ContextVar[Session] = ContextVar("db_session", default=next(get_db()))


def mqtt_client_closure():
    mqtt_client: Client | None = None

    def mqtt_client_func():
        nonlocal mqtt_client
        if mqtt_client is None:
            mqtt_client = get_configured_mqtt_client()
        try:
            yield mqtt_client
        finally:
            mqtt_client.disconnect()

    return mqtt_client_func


get_mqtt_client = mqtt_client_closure()

mqtt_client_session: ContextVar[Client] = ContextVar(
    "mqtt_client_session", default=next(get_mqtt_client())
)


def redis_closure():
    redis_client: Redis | None = None

    def redis_client_func():
        nonlocal redis_client
        if redis_client is None:
            redis_client = Redis(host=os.getenv("REDIS_HOST"), decode_responses=True)
        yield redis_client

    return redis_client_func


get_redis = redis_closure()

redis_session: ContextVar[Redis] = ContextVar(
    "redis_session", default=next(get_redis())
)

redis_event_loop: ContextVar[uvloop.Loop|None] = ContextVar(
    "redis_event_loop", default=None
)
