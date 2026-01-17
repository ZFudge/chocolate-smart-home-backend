from contextvars import ContextVar
from datetime import datetime as dt

import pytest
from sqlalchemy.orm import Session, sessionmaker

from src import models
from src.database import Base
from src.dependencies import db_session, engine, get_db
from src.main import app


OLDER_DATE = dt.fromisoformat("2025-01-01 00:00:00.000000")
NEWER_DATE = dt.fromisoformat("2025-01-02 00:00:00.000000")


def db_closure():

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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

    db_session.get().query(models.device_tags).delete()
    db_session.get().query(models.Device).delete()
    db_session.get().query(models.DeviceType).delete()
    db_session.get().query(models.Tag).delete()
    db_session.get().commit()

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def populated_test_db(empty_test_db):
    test_db = empty_test_db

    type_1 = models.DeviceType(name="TEST_DEVICE_TYPE_NAME_1")
    type_2 = models.DeviceType(name="TEST_DEVICE_TYPE_NAME_2")

    tag_1 = models.Tag(name="Main Tag")
    tag_2 = models.Tag(name="Other Tag")
    tag_3 = models.Tag(name="Third Tag")

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
        mqtt_id=456,
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
