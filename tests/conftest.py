from contextvars import ContextVar
from datetime import datetime as dt
from unittest.mock import AsyncMock, Mock

import pytest
from paho.mqtt.client import CallbackAPIVersion, Client, MQTT_ERR_SUCCESS, MQTTMessage
from redis.asyncio import Redis
from sqlalchemy.exc import InternalError, ProgrammingError
from sqlalchemy.orm import Session, sessionmaker


from src import models
from src.database import Base
from src.dependencies import (
    db_session,
    engine,
    get_db,
    get_mqtt_client,
    get_redis,
    mqtt_client_session,
    redis_session,
)
from src.main import app

from src.SingletonMeta import SingletonMeta


@pytest.fixture(scope="function", autouse=True)
def singleton_instance_cleanup():
    SingletonMeta._SINGLETONS = {}
    yield


def db_closure():
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db: Session | None = None

    def db_func():
        nonlocal db
        if db is None:
            db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    return db_func


@pytest.fixture
def empty_test_db():
    override_get_db = db_closure()
    app.dependency_overrides[get_db] = override_get_db

    override_db_session: ContextVar[Session] = ContextVar(
        "db_session", default=next(override_get_db())
    )
    db_session.set(next(override_get_db()))
    app.dependency_overrides[db_session] = override_db_session

    yield db_session.get()


@pytest.fixture(autouse=True)
def clear_test_db():
    yield
    try:
        db_session.get().query(models.device_tags).delete()
        db_session.get().query(models.Device).delete()
        db_session.get().query(models.Tag).delete()
        db_session.get().query(models.DeviceType).delete()
        db_session.get().commit()
        Base.metadata.drop_all(bind=engine)
    except (ProgrammingError, InternalError):
        pass


@pytest.fixture
def populated_test_db(empty_test_db):
    test_db = empty_test_db

    type_1 = models.DeviceType(name="TEST_DEVICE_TYPE_NAME_1")
    type_2 = models.DeviceType(name="TEST_DEVICE_TYPE_NAME_2")

    tag_1 = models.Tag(name="Main Tag")
    tag_2 = models.Tag(name="Other Tag")
    tag_3 = models.Tag(name="Third Tag")

    OLDER_DATE = dt.fromisoformat("2025-01-01 00:00:00.000000")
    NEWER_DATE = dt.fromisoformat("2025-01-02 00:00:00.000000")

    device_1 = models.Device(
        mqtt_id=123,
        remote_name="Remote Name 1 - 1",
        name="Test Device Name 1",
        device_type=type_1,
        tags=[tag_1, tag_2],
        last_seen=NEWER_DATE,
        last_update_sent=OLDER_DATE,
    )

    device_2 = models.Device(
        mqtt_id=234,
        remote_name="Remote Name 2 - 2",
        name="Test Device Name 2",
        device_type=type_2,
        last_seen=OLDER_DATE,
        last_update_sent=NEWER_DATE,
    )

    test_db.add(type_1)
    test_db.add(type_2)
    test_db.add(tag_1)
    test_db.add(tag_2)
    test_db.add(tag_3)
    test_db.add(device_1)
    test_db.add(device_2)

    test_db.commit()

    yield test_db


def mqtt_client_closure():
    mqtt_client: Client | None = None

    def mqtt_client_func():
        nonlocal mqtt_client
        if mqtt_client is None:
            mqtt_client = Mock(
                spec=Client(
                    CallbackAPIVersion.VERSION2, client_id="testing_mqtt_client"
                )
            )
            mqtt_client.publish.return_value = (MQTT_ERR_SUCCESS, None)
            mqtt_client.is_connected.return_value = True
        try:
            yield mqtt_client
        finally:
            mqtt_client.disconnect()

    return mqtt_client_func


@pytest.fixture
def mqtt_client():
    override_get_mqtt_client = mqtt_client_closure()
    app.dependency_overrides[get_mqtt_client] = override_get_mqtt_client

    override_mqtt_client_session: ContextVar[Client] = ContextVar(
        "mqtt_client_session", default=next(override_get_mqtt_client())
    )

    mqtt_client_session.set(next(override_get_mqtt_client()))
    app.dependency_overrides[mqtt_client_session] = override_mqtt_client_session

    yield mqtt_client_session.get()


@pytest.fixture
def mqtt_message():
    message = MQTTMessage()
    message.payload = b"123,test_device_type_name,test_remote_name"
    yield message


def redis_closure():
    redis_client: Redis | None = None

    def redis_client_func():
        nonlocal redis_client
        if redis_client is None:
            redis_client = AsyncMock(spec=Redis)
            redis_client.xadd = AsyncMock()

        yield redis_client

    return redis_client_func


@pytest.fixture
def redis_client():
    override_get_redis = redis_closure()
    app.dependency_overrides[get_redis] = override_get_redis

    override_redis_session: ContextVar[Redis] = ContextVar(
        "redis_session", default=next(override_get_redis())
    )

    redis_session.set(next(override_get_redis()))
    app.dependency_overrides[redis_session] = override_redis_session

    yield redis_session.get()
